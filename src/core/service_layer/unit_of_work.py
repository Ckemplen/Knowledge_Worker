import core.adapters.repository as repository
import abc
import core.config as config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DEFAULT_SESSION_FACTORY = sessionmaker( 
    bind=create_engine(
        f"sqlite:///{config.DATABASE_PATH}", # echo=config.DB_ECHO
    )
)


class AbstractUnitOfWork(abc.ABC):
    documents: repository.AbstractRepository
    comments: repository.AbstractRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        for repository in [self.documents, self.comments]:
            for object in repository.seen:
                while object.events:
                    yield object.events.pop(0)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
    

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        super().__init__()  # Initialize the base class
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()  
        self.documents = repository.SqlAlchemyDocumentRepository(self.session) 
        self.comments = repository.SqlAlchemyCommentRepository(self.session)
        return self  # Return self to use the context manager

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def _commit(self):
        return self.commit()

    def rollback(self):
        self.session.rollback()


class FakeUnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        super().__init__()  # Initialize the base class
        self.committed = False

    def __enter__(self):
        self.documents = repository.FakeDocumentRepository(documents=[]) 
        self.comments = repository.FakeCommentRepository(comments=[])
        return self  # Return self to use the context manager

    def __exit__(self, *args):
        super().__exit__(*args)

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
