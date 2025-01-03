import core.domain.commands as commands
import core.domain.events as events
from core.domain.model import Document, Entity, RawEntity
from typing import List
import core.service_layer.unit_of_work as uow
from core.adapters.llm_connectors import DocumentAnalysisResponse, CanonicalEntityResponse, AbstractConnector



def add_new_document(
        cmd: commands.CreateDocument, 
        uow: uow.AbstractUnitOfWork,
        ) -> Document:
    
    with uow:
        try:
            sorted_documents = sorted(uow.documents.list(), key=lambda d: d.version, reverse=True)
            existing_doc = next((d for d in sorted_documents if d.filepath == cmd.filepath), None)        
            if existing_doc is not None:
                cmd.version = existing_doc.version + 1
                cmd.previous_version_id = existing_doc.id

            new_doc = uow.documents.add(cmd)

            #uow.collect_new_events()
        except Exception as e:
            print(e)
            print("Error adding new document.")

        finally:
            uow.commit()  

        return new_doc
    

def log_document_creation(*args, **kwargs):
    print("Document created 🥳")

def log_document_processed(*args, **kwargs):
    print("Document processed 🙌")

def add_document_comments(
        event: events.DocumentCreated,
        uow: uow.AbstractUnitOfWork,
):
    with uow:
        for comment in event.comments:
            try:
                uow.comments.add(comment)

            except Exception as e:
                print(f"Error occurred adding comments to db.")
                print(e)
                uow.rollback()
            finally:
                uow.commit()

def get_document_topics_entities_and_summary(
        event: events.DocumentCreated,
        uow: uow.AbstractUnitOfWork,
        document_analysis_connector: AbstractConnector
):
    with uow:
        try:
            doc: Document = uow.documents.get(reference=event.document_id)

            response: DocumentAnalysisResponse = document_analysis_connector.generate(
                document_text=doc.text
            )

            entities = response["document_analysis"]["entities"]
            topics = response['document_analysis']['topics']
            
            for entity in entities:
                uow.raw_entities.add(dict(
                        document_id = doc.id,
                        entity_name = entity['name'],
                        entity_description = entity['description'],
                        entity_prevalence = entity['prevalence']
                ))

            for topic in topics:
                uow.raw_topics.add(dict(
                        document_id = doc.id,
                        topic_name = topic['name'],
                        topic_description = topic['description'],
                        topic_prevalence = topic['prevalence']
                ))
                if topic['subtopics']:
                    for subtopic in topic['subtopics']:
                        uow.raw_topics.add(dict(
                            document_id = doc.id,
                            topic_name = subtopic['name'],
                            topic_description = subtopic['description'],
                            topic_prevalence = subtopic['prevalence']
                    ))
                        
            doc.summary = response['document_analysis']['summary']
            uow.documents.update(updated_obj=doc, fields=['summary'])

            doc.events.append(events.DocumentProcessed(document_id=doc.id))
            uow.documents.update(updated_obj=doc, fields=['no ORM field to update, just adding an event to the uow...'])            

        except Exception as e:
            print(f"Error occurred getting topics, entities and summary.")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


def consolidate_canonical_entities(event: commands.ConsolidateCanonicalEntities,
                                   uow: uow.AbstractUnitOfWork,
                                   canonical_entity_consolidation_connector: AbstractConnector,):
    with uow:
        try:
            raw_entities = uow.raw_entities.list()
            entities = uow.entities.list()

            if raw_entities is not None:
                raw_entities = [_ for _ in raw_entities if _.id in event.raw_entity_ids]

            if entities is not None:
                entities = [_ for _ in entities if _.id in event.entity_ids]

            reviewed_canon_entities: CanonicalEntityResponse = canonical_entity_consolidation_connector.generate(
                existing_canonical_entities=[dict(entity) for entity in entities],
                raw_entities=[dict(raw_entity) for raw_entity in raw_entities]
            )

            for _ in reviewed_canon_entities:
                existing_canon_entity = uow.entities.get(reference=_.canonical_entity_id)
                if existing_canon_entity:
                    updated_entity = Entity(id=existing_canon_entity.id, entity_description=_.description, entity_name=_.name)
                    uow.entities.update(updated_obj=updated_entity, fields=['entity_name', 'entity_description'])
                    
                    linked_raw_entities = uow.entities.get_raw_entities(existing_canon_entity.id)
                    for reviewed_id in _.raw_entity_ids:
                        if reviewed_id not in [lre.id for lre in linked_raw_entities]:
                            uow.entities.add_raw_entity(entity_id=existing_canon_entity.id, raw_entity_id=reviewed_id)

                else:
                    new_entity = uow.entities.add({'entity_name': _.name, 'entity_description': _.description})
                    for reviewed_id in _.raw_entity_ids:
                        uow.entities.add_raw_entity(entity_id=new_entity.id, raw_entity_id=reviewed_id)

        except Exception as e:
            print(f"Error occurred consolidating canonical entities.")
            print(e)
            uow.rollback()
        finally:
            uow.commit()

EVENT_HANDLERS = {
   events.DocumentCreated: [
       ("add_document_comments",add_document_comments), 
       ("get_document_topics_entities_and_summary",get_document_topics_entities_and_summary), 
       ("log_document_creation",log_document_creation)],
   events.CommentCreated: [],
   events.DocumentProcessed: [("log_document_processed",log_document_processed)],
}

COMMAND_HANDLERS = {
    commands.CreateDocument: ("add_new_document", add_new_document),
    commands.ConsolidateCanonicalEntities: ("consolidate_canonical_entities", consolidate_canonical_entities)
}
