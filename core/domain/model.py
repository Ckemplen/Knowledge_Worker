from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, NamedTuple
from . import events
from dataclasses import dataclass


class BaseDomainModel(BaseModel):
    created_at: datetime
    last_modified_at: datetime
    created_by: str
    last_modified_by: str
    version: int = 1

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class DomainDataclass:
    created_at: datetime
    last_modified_at: datetime
    created_by: str
    last_modified_by: str
    version: int = 1


class Document(BaseDomainModel):
    id: int
    filepath: str
    filename: str
    filetype: Optional[str] = None
    text: str
    html_text: Optional[str] = None
    previous_version_id: Optional[int] = None
    processed_at: datetime
    summary: Optional[str]
    version_comment: Optional[str]
    revision: Optional[int] = 0
    comments: Optional[List["Comment"]] = Field(default_factory=list, exclude=True)
    previous_versions: Optional[List["Document"]] = Field(
        default_factory=list, exclude=True
    )
    next_versions: Optional[List["Document"]] = Field(
        default_factory=list, exclude=True
    )
    raw_topics: Optional[List["RawTopic"]] = []
    document_topics: Optional[List["DocumentTopic"]] = []
    raw_entities: Optional[List["RawEntity"]] = []
    document_entities: Optional[List["DocumentEntity"]] = []
    entities: Optional[List["Entity"]] = []
    events: Optional[List] = []

    def compose_DocumentCreated_event(self, doc_comments) -> None:
        if doc_comments is not None:
            docx_comments = [DocxComment(*c) for c in doc_comments]
            self.events.append(
                events.DocumentCreated(
                    document_id=self.id,
                    comments=[
                        {
                            "document_id": self.id,
                            "reference_text": c.reference_text,
                            "author": c.author,
                            "comment_date": datetime.strptime(
                                c.date, "%Y-%m-%dT%H:%M:%SZ"
                            ),
                            "comment_text": c.comment_text,
                        }
                        for c in docx_comments
                    ],
                )
            )
        return None

    def __hash__(self):
        return hash((self.id, self.filepath, self.filename, self.version))

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            "Document": lambda v: v.dict(
                exclude={"next_versions", "previous_versions", "comments"}
            ),
            datetime: lambda v: v.isoformat(),
        }


class Comment(BaseDomainModel):
    id: int
    document_id: int
    author: str
    reference_text: str
    comment_text: str
    comment_date: datetime
    events: Optional[List] = []

    def __hash__(self):
        return hash((self.id, self.document_id, self.author, self.comment_date))

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class RawTopic(BaseDomainModel):
    id: int
    document_id: int
    topic_name: str
    topic_description: str
    topic_prevalence: int
    events: Optional[List] = []

    def __hash__(self):
        return hash((self.id, self.document_id, self.topic_description))


class Topic(BaseDomainModel):
    id: int
    topic_name: str
    topic_description: str
    document_topics: Optional[List["DocumentTopic"]] = []
    raw_topics: Optional[List["TopicRawTopic"]] = []
    events: Optional[List] = []

    def __hash__(self):
        return hash((self.id, self.topic_description))


class RawEntity(BaseDomainModel):
    id: int
    document_id: int
    entity_name: str
    entity_description: str
    entity_prevalence: int
    events: Optional[List] = []

    def __hash__(self):
        return hash((self.id, self.document_id, self.entity_description))


class Entity(BaseDomainModel):
    id: int
    entity_name: str
    entity_description: str
    documents: Optional[List["Document"]] = []
    events: Optional[List] = []

    def __hash__(self):
        return hash((self.id, self.entity_name, self.entity_description))


class Stakeholder(BaseDomainModel):
    id: int
    stakeholder_name: str
    stakeholder_type: str
    stakeholder_description: str

    def __hash__(self):
        return hash(
            (
                self.id,
                self.stakeholder_name,
                self.stakeholder_type,
                self.stakeholder_description,
            )
        )


@dataclass
class DocumentTopic(DomainDataclass):
    document_id: int
    topic_id: int
    link_description: str

    def __hash__(self):
        return hash((self.topic_id, self.document_id))


@dataclass
class TopicRawTopic(DomainDataclass):
    topic_id: int
    raw_topic_id: int
    link_description: str

    def __hash__(self):
        return hash((self.topic_id, self.raw_topic_id))


@dataclass
class DocumentEntity(DomainDataclass):
    document_id: int
    entity_id: int
    link_description: str

    def __hash__(self):
        return hash((self.entity_id, self.document_id))


@dataclass
class EntityRawEntity(DomainDataclass):
    entity_id: int
    raw_entity_id: int
    link_description: str

    def __hash__(self):
        return hash((self.entity_id, self.raw_entity_id))


class DocxComment(NamedTuple):
    reference_text: str
    author: str
    date: str
    comment_text: str
