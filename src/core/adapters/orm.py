from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, MetaData
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

import core.config as config

metadata = MetaData()

Base = declarative_base()

class DocumentORM(Base):
    __tablename__ = 'Documents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    filepath = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    filetype = Column(String)
    text = Column(String)
    html_text = Column(String)
    version = Column(Integer, nullable=False, default=1)
    previous_version_id = Column(Integer, ForeignKey('Documents.id'))
    last_modified_at = Column(DateTime)
    created_at = Column(DateTime)
    processed_at = Column(DateTime)
    created_by = Column(String)
    last_modified_by = Column(String)
    summary = Column(String)
    version_comment = Column(String)
    revision = Column(Integer, default=1)
    comments = relationship('CommentORM', back_populates='document')
    previous_version = relationship('DocumentORM', remote_side=[id], back_populates='next_versions')
    next_versions = relationship('DocumentORM', back_populates='previous_version')

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class CommentORM(Base):
    __tablename__ = 'Comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('Documents.id'), nullable=False)
    author = Column(String)
    comment_text = Column(String)
    reference_text = Column(String)
    comment_date = Column(DateTime)
    document = relationship('DocumentORM', back_populates='comments')

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


engine = create_engine(f"sqlite:///{config.DATABASE_PATH}")

metadata.create_all(engine)

Session = sessionmaker(bind=engine)
