import abc
import core.domain.model as model
import core.domain.commands as commands
import core.adapters.orm as orm
import core.domain.events as events
from typing import List, Dict, Union, Any
from datetime import datetime

from dataclasses import asdict

class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()

    def add(self, cmd):
        return_obj: Union[None, orm.DocumentORM, orm.CommentORM] = self._add(cmd)
        self.seen.add(return_obj)
        return return_obj

    def get(self, reference):
        entity = self._get(reference)
        if entity:
            self.seen.add(entity)
        return entity

    @abc.abstractmethod
    def _add(self, entity):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, reference):
        raise NotImplementedError



class SqlAlchemyDocumentRepository(AbstractRepository):
    def __init__(self, session):
        self.seen = set()
        self.session = session
    
    def _add(self, cmd: commands.CreateDocument):
        document = asdict(cmd)
        doc_comments = document.get('doc_comments')
        del document['doc_comments']
        orm_document = orm.DocumentORM(**document)
        self.session.add(orm_document)
        self.session.flush()
        pydantic_document = model.Document(**orm_document.to_dict())
        pydantic_document.compose_DocumentCreated_event(doc_comments)
        return pydantic_document
        

    def _get(self, reference):
        document_obj = self.session.query(orm.DocumentORM).filter_by(id=reference).one()
        return model.Document.model_validate(document_obj)

    def list(self):
        document_objs = self.session.query(orm.DocumentORM).all()
        return [model.Document.model_validate(d) for d in document_objs]
    

    
class SqlAlchemyCommentRepository(AbstractRepository):
    def __init__(self, session):
        self.seen = set()
        self.session = session

    def _add(self, comment: Dict):
        orm_comment = orm.CommentORM(
            document_id=comment['document_id'],
            reference_text=comment['reference_text'],
            comment_text=comment['comment_text'],
            comment_date=comment['comment_date'],
            author=comment['author'],
        )
        self.session.add(orm_comment)
        self.session.flush()
        pydantic_comment = model.Comment(**orm_comment.to_dict())
        return pydantic_comment

    def _get(self, reference):
        comment_obj = self.session.query(orm.CommentORM).filter_by(id=reference).one()
        return model.Comment.model_validate(comment_obj)

    def list(self):
        comment_objs = self.session.query(orm.CommentORM).all()
        return [model.Comment.model_validate(c) for c in comment_objs]
    
