import abc
import core.domain.model as model
import core.domain.commands as commands
import core.adapters.orm as orm
import core.domain.events as events
from typing import List, Dict, Union, Any
from datetime import datetime
import json

from dataclasses import asdict

def log_change(session, entity_name, entity_id, previous_object, revised_object):
    changelog = orm.ChangelogORM(
        previous_object_json=json.dumps(previous_object),
        revised_object_json=json.dumps(revised_object),
        entity_name=entity_name,
        entity_id=entity_id
    )
    session.add(changelog)
    session.flush()
    return None

ORM_OBJECT = Union[None, orm.DocumentEntityORM, orm.DocumentORM, orm.DocumentTopicORM, orm.CommentORM, orm.RawEntityORM, orm.RawTopicORM, orm.TopicRawTopicORM, orm.EntityRawEntityORM]
PYDANTIC_OBJECT = Union[None, model.DocumentEntity, model.Document, model.DocumentTopic, model.Comment, model.RawEntity, model.RawTopic, model.TopicRawTopic, model.EntityRawEntity]
class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()

    def add(self, cmd) -> PYDANTIC_OBJECT:
        return_obj: ORM_OBJECT = self._add(cmd)
        self.seen.add(return_obj)
        return return_obj
    
    def update(self, updated_obj: PYDANTIC_OBJECT, fields: List[str]) -> PYDANTIC_OBJECT:
        original_object: PYDANTIC_OBJECT = self._get(reference=updated_obj.id)
        return_obj: PYDANTIC_OBJECT = self._update(updated_obj, fields)
        self.seen.add(return_obj) # Still use this to get any events added to the revised entity object.
        # Log the change
        log_change(
            self.session,
            source_table_name=updated_obj.__class__.__name__,
            source_id=updated_obj.id,
            previous_object=original_object.model_dump(),
            revised_object=return_obj.model_dump()
        )
        
        return return_obj

    def get(self, reference) -> PYDANTIC_OBJECT:
        entity = self._get(reference)
        if entity:
            self.seen.add(entity)
        return entity
    
    def list(self) -> List[PYDANTIC_OBJECT]:
        objects_list: List[PYDANTIC_OBJECT] = self._list()
        for object in objects_list:
            self.seen.add(object)
        return objects_list

    @abc.abstractmethod
    def _add(self, entity):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, reference):
        raise NotImplementedError
    
    @abc.abstractmethod
    def _list(self):
        raise NotImplementedError



class SqlAlchemyDocumentRepository(AbstractRepository):
    def __init__(self, session):
        self.seen = set()
        self.session = session
    
    def _add(self, cmd: commands.CreateDocument) -> model.Document:
        document = asdict(cmd)
        doc_comments = document.get('doc_comments')
        del document['doc_comments']
        orm_document = orm.DocumentORM(**document)
        self.session.add(orm_document)
        self.session.flush()
        pydantic_document = model.Document(**orm_document.to_dict())
        pydantic_document.compose_DocumentCreated_event(doc_comments)
        return pydantic_document
    
    def _update(self, updated_obj: model.Document, fields: List[str]):
        document_obj: ORM_OBJECT = self.session.query(orm.DocumentORM).filter_by(id=updated_obj.id).one()
        
        for key, value in dict(updated_obj).items():
            if key not in fields:
                continue
            setattr(document_obj, key, value)

        self.session.commit()

        return updated_obj
        
    def _get(self, reference) -> model.Document:
        document_obj = self.session.query(orm.DocumentORM).filter_by(id=reference).one()
        document_dict = document_obj.to_dict()
        document_dict.pop('next_versions', None)
        document_dict.pop('previous_versions', None)
        return model.Document.model_validate(document_dict)

    def _list(self) -> List[model.Document]:
        document_objs = self.session.query(orm.DocumentORM).all()
        documents = []
        for d in document_objs:
            document_dict = d.to_dict()
            document_dict.pop('next_versions', None)
            document_dict.pop('previous_versions', None)
            documents.append(model.Document.model_validate(document_dict))
        return documents
        

    
class SqlAlchemyCommentRepository(AbstractRepository):
    def __init__(self, session):
        self.seen = set()
        self.session = session

    def _add(self, comment: Dict):
        orm_comment = orm.CommentORM(**comment)
        self.session.add(orm_comment)
        self.session.flush()
        pydantic_comment = model.Comment(**orm_comment.to_dict())
        return pydantic_comment

    def _get(self, reference):
        comment_obj = self.session.query(orm.CommentORM).filter_by(id=reference).one()
        return model.Comment.model_validate(comment_obj)

    def _list(self):
        comment_objs = self.session.query(orm.CommentORM).all()
        return [model.Comment.model_validate(c) for c in comment_objs]
    
    
class SqlAlchemyRawTopicsRepository(AbstractRepository):
    def __init__(self, session):
        self.seen = set()
        self.session = session

    def _add(self, raw_topic: Dict):
        orm_raw_topic = orm.RawTopicORM(**raw_topic)
        self.session.add(orm_raw_topic)
        self.session.flush()
        pydantic_raw_topic = model.RawTopic(**orm_raw_topic.to_dict())
        return pydantic_raw_topic

    def _get(self, reference):
        raw_topic_obj = self.session.query(orm.RawTopicORM).filter_by(id=reference).one()
        return model.RawTopic.model_validate(raw_topic_obj)

    def _list(self):
        raw_topic_objs = self.session.query(orm.RawTopicORM).all()
        return [model.RawTopic.model_validate(r_t) for r_t in raw_topic_objs]

    
class SqlAlchemyRawEntitiesRepository(AbstractRepository):
    def __init__(self, session):
        self.seen = set()
        self.session = session

    def _add(self, raw_entity: Dict):
        orm_raw_entity = orm.RawEntityORM(**raw_entity)
        self.session.add(orm_raw_entity)
        self.session.flush()
        pydantic_raw_entity = model.RawEntity(**orm_raw_entity.to_dict())
        return pydantic_raw_entity

    def _get(self, reference):
        raw_entity_obj = self.session.query(orm.RawEntityORM).filter_by(id=reference).one()
        return model.RawEntity.model_validate(raw_entity_obj)

    def _list(self):
        raw_entity_objs = self.session.query(orm.RawEntityORM).all()
        return [model.RawEntity.model_validate(r_e) for r_e in raw_entity_objs]
    


class SqlAlchemyTopicsRepository(AbstractRepository):
    def __init__(self, session):
        self.seen = set()
        self.session = session

    def _add(self, _topic: Dict):
        orm_topic = orm.TopicORM(**_topic)
        self.session.add(orm_topic)
        self.session.flush()
        pydantic_topic = model.Topic(**orm_topic.to_dict())
        return pydantic_topic

    def _get(self, reference):
        _topic_obj = self.session.query(orm.TopicORM).filter_by(id=reference).one()
        return model.Topic.model_validate(_topic_obj)

    def _list(self):
        _topic_objs = self.session.query(orm.TopicORM).all()
        return [model.Topic.model_validate(r_t) for r_t in _topic_objs]

    
class SqlAlchemyEntitiesRepository(AbstractRepository):
    def __init__(self, session):
        self.seen = set()
        self.session = session

    def _add(self, _entity: Dict):
        orm_entity = orm.EntityORM(**_entity)
        self.session.add(orm_entity)
        self.session.flush()
        pydantic_entity = model.Entity(**orm_entity.to_dict())
        return pydantic_entity

    def _get(self, reference):
        entity_obj = self.session.query(orm.EntityORM).filter_by(id=reference).one()
        return model.Entity.model_validate(entity_obj)

    def get_raw_entities(self, reference) -> orm.RawEntityORM:
        entity_obj = self.session.query(orm.EntityORM).filter_by(id=reference).one()
        raw_entities: orm.RawEntityORM = entity_obj.raw_entities
        return raw_entities
    
    def add_raw_entity(self, entity_id, raw_entity_id):
        new_link = orm.EntityRawEntityORM(entity_id=entity_id, raw_entity_id=raw_entity_id)
        self.session.add(new_link)
        self.session.flush()

    def _list(self):
        entity_objs = self.session.query(orm.EntityORM).all()
        return [model.Entity.model_validate(r_e) for r_e in entity_objs]
    
    def _update(self, updated_obj: model.Entity, fields: List[str]):
        entity_obj: ORM_OBJECT = self.session.query(orm.EntityORM).filter_by(id=updated_obj.id).one()
        
        for key, value in dict(updated_obj).items():
            if key not in fields:
                continue
            setattr(entity_obj, key, value)

        self.session.commit()

        return updated_obj
    