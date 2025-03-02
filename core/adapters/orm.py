from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    MetaData,
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import datetime
import core.config

metadata = MetaData()

Base = declarative_base()


class BaseWithToDict(Base):
    __abstract__ = True

    # Adds to_dict method
    def to_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


class BaseAudit(BaseWithToDict):
    __abstract__ = True

    # Adds audit fields to all inheriting models
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    last_modified_at = Column(
        DateTime, onupdate=datetime.datetime.now(datetime.timezone.utc)
    )
    created_by = Column(String)
    last_modified_by = Column(String)
    version = Column(Integer, nullable=False, default=1)


class DocumentORM(BaseAudit):
    __tablename__ = "Documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filepath = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    filetype = Column(String)
    text = Column(String)
    html_text = Column(String)
    previous_version_id = Column(Integer, ForeignKey("Documents.id"))
    last_modified_by = Column(String)
    summary = Column(String)
    version_comment = Column(String)
    revision = Column(Integer, default=1)
    comments = relationship("CommentORM", back_populates="document")
    previous_version = relationship(
        "DocumentORM", remote_side=[id], back_populates="next_versions"
    )
    next_versions = relationship("DocumentORM", back_populates="previous_version")


class RawTopicORM(BaseAudit):
    __tablename__ = "RawTopics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("Documents.id"), nullable=False)
    topic_name = Column(String)
    topic_description = Column(String)
    topic_prevalence = Column(Integer)
    document = relationship("DocumentORM", back_populates="raw_topics")
    topics = relationship("TopicRawTopicORM", back_populates="raw_topic")


class TopicORM(BaseAudit):
    __tablename__ = "Topics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_name = Column(String)
    topic_description = Column(String)
    document_topics = relationship("DocumentTopicORM", back_populates="topic")
    raw_topics = relationship("TopicRawTopicORM", back_populates="topic")


class RawEntityORM(BaseAudit):
    __tablename__ = "RawEntities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("Documents.id"), nullable=False)
    entity_name = Column(String)
    entity_description = Column(String)
    entity_prevalence = Column(Integer)
    document = relationship("DocumentORM", back_populates="raw_entities")
    entities = relationship("EntityRawEntityORM", back_populates="raw_entity")


class EntityORM(BaseAudit):
    __tablename__ = "Entities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_name = Column(String)
    entity_description = Column(String)
    document_entities = relationship("DocumentEntityORM", back_populates="entity")
    raw_entities = relationship("EntityRawEntityORM", back_populates="entity")


class StakeholderORM(BaseAudit):
    __tablename__ = "Stakeholders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    stakeholder_name = Column(String)
    stakeholder_type = Column(String)
    stakeholder_description = Column(String)


class DocumentTopicORM(BaseAudit):
    __tablename__ = "DocumentTopics"
    document_id = Column(Integer, ForeignKey("Documents.id"), primary_key=True)
    topic_id = Column(Integer, ForeignKey("Topics.id"), primary_key=True)
    link_description = Column(String)
    document = relationship("DocumentORM", back_populates="document_topics")
    topic = relationship("TopicORM", back_populates="document_topics")


class TopicRawTopicORM(BaseAudit):
    __tablename__ = "TopicsRawTopics"
    topic_id = Column(Integer, ForeignKey("Topics.id"), primary_key=True)
    raw_topic_id = Column(Integer, ForeignKey("RawTopics.id"), primary_key=True)
    link_description = Column(String)
    topic = relationship("TopicORM", back_populates="raw_topics")
    raw_topic = relationship("RawTopicORM", back_populates="topics")


class CommentORM(BaseAudit):
    __tablename__ = "Comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("Documents.id"), nullable=False)
    author = Column(String)
    comment_text = Column(String)
    reference_text = Column(String)
    comment_date = Column(DateTime)
    document = relationship("DocumentORM", back_populates="comments")


class DocumentEntityORM(BaseAudit):
    __tablename__ = "DocumentEntities"
    document_id = Column(Integer, ForeignKey("Documents.id"), primary_key=True)
    entity_id = Column(Integer, ForeignKey("Entities.id"), primary_key=True)
    link_description = Column(String)
    document = relationship("DocumentORM", back_populates="document_entities")
    entity = relationship("EntityORM", back_populates="document_entities")


class EntityRawEntityORM(BaseAudit):
    __tablename__ = "EntitiesRawEntities"
    entity_id = Column(Integer, ForeignKey("Entities.id"), primary_key=True)
    raw_entity_id = Column(Integer, ForeignKey("RawEntities.id"), primary_key=True)
    link_description = Column(String)
    entity = relationship("EntityORM", back_populates="raw_entities")
    raw_entity = relationship("RawEntityORM", back_populates="entities")


class ChangelogORM(
    BaseWithToDict
):  # Not inheriting BaseORM because audit fields not needed
    __tablename__ = "changelogs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    modified_datetime = Column(
        DateTime, default=datetime.datetime.now(datetime.timezone.utc)
    )
    previous_object_json = Column(String)
    revised_object_json = Column(String)
    entity_name = Column(String)
    entity_id = Column(Integer)


DocumentORM.raw_topics = relationship("RawTopicORM", back_populates="document")
DocumentORM.document_topics = relationship(
    "DocumentTopicORM", back_populates="document"
)
DocumentORM.raw_entities = relationship("RawEntityORM", back_populates="document")
DocumentORM.document_entities = relationship(
    "DocumentEntityORM", back_populates="document"
)


engine = create_engine(f"sqlite:///{core.config.DATABASE_PATH}")

metadata.create_all(engine)

Session = sessionmaker(bind=engine)
