import core.domain.commands as commands
import core.domain.events as events
from core.domain.model import Topic
from core.domain.model import (
    Document,
    Entity,
    EntityRawEntity,
    DocumentEntity,
    Stakeholder,
    Topic,
)
import core.domain.error_messages
import core.service_layer.unit_of_work as uow
from core.adapters.llm_connectors import (
    DocumentAnalysisResponse,
    CanonicalEntityResponse,
    AbstractConnector,
)
import json
from dataclasses import asdict


def add_new_document(
    cmd: commands.CreateDocument,
    uow: uow.AbstractUnitOfWork,
) -> Document:
    with uow:
        try:
            sorted_documents = sorted(
                uow.documents.list(), key=lambda d: d.version, reverse=True
            )
            existing_doc = next(
                (d for d in sorted_documents if d.filepath == cmd.filepath), None
            )
            if existing_doc is not None:
                cmd.version = existing_doc.version + 1
                cmd.previous_version_id = existing_doc.id

            new_doc = uow.documents.add(cmd)

            # uow.collect_new_events()
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
                print("Error occurred adding comments to db.")
                print(e)
                uow.rollback()
            finally:
                uow.commit()


def get_document_topics_entities_and_summary(
    event: events.DocumentCreated,
    uow: uow.AbstractUnitOfWork,
    document_analysis_connector: AbstractConnector,
):
    with uow:
        try:
            doc: Document = uow.documents.get(reference=event.document_id)

            response: DocumentAnalysisResponse = document_analysis_connector.generate(
                document_text=doc.text
            )

            entities = response["document_analysis"]["entities"]
            topics = response["document_analysis"]["topics"]

            for entity in entities:
                uow.raw_entities.add(
                    dict(
                        document_id=doc.id,
                        entity_name=entity["name"],
                        entity_description=entity["description"],
                        entity_prevalence=entity["prevalence"],
                    )
                )

            for topic in topics:
                uow.raw_topics.add(
                    dict(
                        document_id=doc.id,
                        topic_name=topic["name"],
                        topic_description=topic["description"],
                        topic_prevalence=topic["prevalence"],
                    )
                )
                if topic["subtopics"]:
                    for subtopic in topic["subtopics"]:
                        uow.raw_topics.add(
                            dict(
                                document_id=doc.id,
                                topic_name=subtopic["name"],
                                topic_description=subtopic["description"],
                                topic_prevalence=subtopic["prevalence"],
                            )
                        )

            doc.summary = response["document_analysis"]["summary"]
            uow.documents.update(updated_obj=doc, fields=["summary"])

            doc.events.append(events.DocumentProcessed(document_id=doc.id))
            uow.documents.update(
                updated_obj=doc,
                fields=["no ORM field to update, just adding an event to the uow..."],
            )

        except Exception as e:
            print("Error occurred getting topics, entities and summary.")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


def consolidate_canonical_entities(
    event: commands.ConsolidateCanonicalEntities,
    uow: uow.AbstractUnitOfWork,
    canonical_entity_consolidation_connector: AbstractConnector,
):
    with uow:
        try:
            # raw_entities = filter_entities(uow.raw_entities.list(), event.raw_entity_ids)
            # entities = filter_entities(uow.entities.list(), event.entity_ids)

            # reviewed_canon_entities: CanonicalEntityResponse = canonical_entity_consolidation_connector.generate(
            #     existing_canonical_entities=[dict(entity) for entity in entities],
            #     raw_entities=[dict(raw_entity) for raw_entity in raw_entities]
            # )

            reviewed_canon_entities = load_reviewed_canon_entities()

            for reviewed_canon_entity in reviewed_canon_entities:
                try:
                    process_reviewed_entity(reviewed_canon_entity, uow)
                except core.domain.error_messages.EntityProcessingError as e:
                    print(
                        f"Error processing entity: {e}\n\n{reviewed_canon_entity}\n\n\n"
                    )
                    uow.rollback()
                    continue

        except Exception as e:
            print("Error occurred consolidating canonical entities.")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


def filter_entities(entities, ids):
    try:
        if ids is not None:
            return [entity for entity in entities if entity.id in ids]
        return entities
    except Exception as e:
        raise core.domain.error_messages.EntityProcessingError(
            f"Error filtering entities: {e}"
        )


def load_reviewed_canon_entities():
    try:
        with open(
            "C:\\Users\\ckemplen\\POLICY_DEVELOPMENT_APP\\test_canon_outputs.json", "r"
        ) as file:
            return json.load(file)
    except Exception as e:
        raise core.domain.error_messages.EntityProcessingError(
            f"Error loading reviewed canonical entities: {e}"
        )


def process_reviewed_entity(reviewed_canon_entity, uow):
    try:
        if reviewed_canon_entity.get("canonical_entity_id") is not None:
            existing_canon_entity = uow.entities.get(
                reference=reviewed_canon_entity.get("canonical_entity_id")
            )
            if existing_canon_entity is None:
                new_entity = create_new_entity(reviewed_canon_entity, uow)
                link_raw_entities(
                    new_entity.id, reviewed_canon_entity["raw_entity_ids"], uow
                )
                new_entity.events.append(
                    events.ExistingCanonicalEntityHallucination(
                        item=reviewed_canon_entity, entity_id=new_entity.id
                    )
                )
                uow.entities.update(
                    new_entity,
                    fields=["No fields to update, just sending up the event."],
                )
            else:
                update_existing_entity(
                    existing_canon_entity, reviewed_canon_entity, uow
                )
        else:
            new_entity = create_new_entity(reviewed_canon_entity, uow)
            link_raw_entities(
                new_entity.id, reviewed_canon_entity["raw_entity_ids"], uow
            )
            link_document_entities(new_entity.id, uow)
    except Exception as e:
        raise core.domain.error_messages.EntityProcessingError(
            f"Error processing reviewed entity: {e}"
        )


def create_new_entity(reviewed_canon_entity, uow):
    try:
        return uow.entities.add(
            {
                "entity_name": reviewed_canon_entity["name"],
                "entity_description": reviewed_canon_entity["description"],
            }
        )
    except Exception as e:
        raise core.domain.error_messages.EntityCreationError(
            f"Error creating new entity: {e}"
        )


def add_entity(cmd: commands.AddEntity, uow: uow.AbstractUnitOfWork):
    print("Using add_entity handler.")
    with uow:
        try:
            uow.entities.add(
                dict(
                    entity_name=cmd.entity_name,
                    entity_description=cmd.entity_description,
                    created_at=cmd.created_at,
                    created_by=cmd.created_by,
                    last_modified_at=cmd.last_modified_at,
                    last_modified_by=cmd.last_modified_by,
                )
            )
        except Exception as e:
            print("Error occurred adding entity.")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


def update_existing_entity(
    existing_canon_entity: Entity, reviewed_canon_entity: CanonicalEntityResponse, uow
):
    if existing_canon_entity.entity_name != reviewed_canon_entity["name"]:
        existing_canon_entity.events.append(
            events.ExistingCanonicalEntityHallucination(
                item=reviewed_canon_entity, entity_id=existing_canon_entity.id
            )
        )
        uow.entities.update(
            existing_canon_entity,
            fields=["No fields to update, just sending up the event."],
        )
        raise core.domain.error_messages.EntityUpdateError(
            f"Name of existing entity {existing_canon_entity.entity_name} does not match attempted update name {reviewed_canon_entity['name']}"
        )
    try:
        updated_entity = Entity(
            id=existing_canon_entity.id,
            entity_description=reviewed_canon_entity["description"],
            entity_name=reviewed_canon_entity["name"],
        )
        uow.entities.update(
            updated_obj=updated_entity, fields=["entity_name", "entity_description"]
        )
        link_raw_entities(
            existing_canon_entity.id, reviewed_canon_entity["raw_entity_ids"], uow
        )
    except Exception as e:
        raise core.domain.error_messages.EntityUpdateError(
            f"Error updating existing entity: {e}"
        )


def link_raw_entities(entity_id, raw_entity_ids, uow):
    try:
        linked_raw_entities = uow.entities.get_raw_entities(entity_id)
        for reviewed_id in raw_entity_ids:
            if reviewed_id not in [
                linked_entity.raw_entity_id for linked_entity in linked_raw_entities
            ]:
                new_raw_entity = EntityRawEntity(
                    entity_id=entity_id, raw_entity_id=reviewed_id, link_description="",
                )
                uow.entities.add_raw_entity(new_raw_entity)
    except Exception as e:
        raise core.domain.error_messages.EntityProcessingError(
            f"Error linking raw entities: {e}"
        )


def link_document_entities(entity_id, uow):
    try:
        linked_raw_entities = uow.entities.get_raw_entities(entity_id)
        for linked_raw_entity in linked_raw_entities:
            doc_id = linked_raw_entity.raw_entity.document_id
            new_document_entity_link = DocumentEntity(
                document_id=doc_id, entity_id=entity_id, link_description=""
            )
            uow.entities.add_document_entity(new_document_entity_link)
    except Exception as e:
        raise core.domain.error_messages.EntityProcessingError(
            f"Error linking document entities: {e}"
        )


def log_hallucination(event: events.ExistingCanonicalEntityHallucination):
    print("Hallucination identified and captured by event!")
    print("Item: ", event.item)
    print("New entity id: ", event.entity_id)


def add_stakeholder(cmd: commands.AddStakeholder, uow: uow.AbstractUnitOfWork):
    print("Using add_stakeholder handler.")
    with uow:
        try:
            uow.stakeholders.add(cmd)
        except Exception as e:
            print("Error occurred adding stakeholder.")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


def update_stakeholder(cmd: commands.UpdateStakeholder, uow: uow.AbstractUnitOfWork):
    with uow:
        try:
            updated_stakeholder = Stakeholder(**asdict(cmd))
            uow.stakeholders.update(
                updated_obj=updated_stakeholder,
                fields=[
                    "stakeholder_name",
                    "stakeholder_type",
                    "version",
                    "stakeholder_description",
                    "last_modified_by",
                    "last_modified_at",
                ],
            )
        except Exception as e:
            print("Error occured updating stakeholder.")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


def update_entity(cmd: commands.UpdateEntity, uow: uow.AbstractUnitOfWork):
    with uow:
        try:
            updated_entity = Entity(**asdict(cmd))
            uow.entities.update(
                updated_obj=updated_entity, fields=["entity_name", "entity_description"]
            )
        except Exception as e:
            print("Error occured updating stakeholder.")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


def update_document_summary(
    cmd: commands.UpdateDocumentSummary, uow: uow.AbstractUnitOfWork
):
    with uow:
        try:
            current_doc = uow.documents.get(reference=id)
            update_dict = current_doc.to_dict()
            update_dict["summary"] = cmd.summary
            updated_doc = Document(**update_dict)
            uow.entities.update(updated_obj=updated_doc, fields=["summary"])
        except Exception as e:
            print("Error occured updating document.")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


def create_topic(cmd: commands.CreateTopic, uow: uow.AbstractUnitOfWork):
    with uow:
        try:
            topic: Topic = uow.topics.add(
                {
                    "topic_name": cmd.topic_name,
                    "topic_description": cmd.topic_description,
                }
            )
            print("New topic added: ", topic)
        except Exception as e:
            print("Error creating topic")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


def update_topic(cmd: commands.UpdateTopic, uow: uow.AbstractUnitOfWork):
    with uow:
        try:
            topic = Topic(
                id=cmd.id,
                topic_name=cmd.topic_name,
                topic_description=cmd.topic_description,
            )
            uow.topics.update(topic, ["topic_name", "topic_description"])
        except Exception as e:
            print("Error updating topic")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


def delete_topic(cmd: commands.DeleteTopic, uow: uow.AbstractUnitOfWork):
    with uow:
        try:
            uow.topics.delete(cmd.id)
        except Exception as e:
            print("Error deleting topic")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


def delete_stakeholder(cmd: commands.DeleteStakeholder, uow: uow.AbstractUnitOfWork):
    with uow:
        try:
            uow.stakeholders.delete(cmd.id)
        except Exception as e:
            print("Error deleting stakeholder")
            print(e)
            uow.rollback()
        finally:
            uow.commit()


EVENT_HANDLERS = {
    events.DocumentCreated: [
        ("add_document_comments", add_document_comments),
        (
            "get_document_topics_entities_and_summary",
            get_document_topics_entities_and_summary,
        ),
        ("log_document_creation", log_document_creation),
    ],
    events.CommentCreated: [],
    events.DocumentProcessed: [("log_document_processed", log_document_processed)],
    events.ExistingCanonicalEntityHallucination: [
        ("log_hallucination", log_hallucination)
    ],
}

COMMAND_HANDLERS = {
    commands.AddStakeholder: ("add_stakeholder", add_stakeholder),
    commands.UpdateStakeholder: ("update_stakeholder", update_stakeholder),
    commands.AddEntity: ("add_entity", add_entity),
    commands.UpdateEntity: ("update_entity", update_entity),
    commands.UpdateDocumentSummary: (
        "update_document_summary",
        update_document_summary,
    ),
    commands.CreateDocument: ("add_new_document", add_new_document),
    commands.ConsolidateCanonicalEntities: (
        "consolidate_canonical_entities",
        consolidate_canonical_entities,
    ),
    commands.CreateTopic: ("create_topic", create_topic),
    commands.UpdateTopic: ("update_topic", update_topic),
    commands.DeleteTopic: ("delete_topic", delete_topic),
    commands.DeleteStakeholder: ("delete_stakeholder", delete_stakeholder),
}
