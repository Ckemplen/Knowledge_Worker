from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, NamedTuple
from . import events

class Document(BaseModel):
    id: int
    filepath: str
    filename: str
    filetype: Optional[str] = None
    version: int = 1
    text: str
    html_text: Optional[str] = None
    previous_version_id: Optional[int] = None
    last_modified_at: datetime
    created_at: datetime
    processed_at: datetime
    created_by: str
    last_modified_by: str
    summary: Optional[str]
    version_comment: Optional[str]
    revision: Optional[int] = 0
    comments: Optional[List['Comment']] = Field(default_factory=list, exclude=True)
    previous_versions: Optional[List['Document']] = Field(default_factory=list, exclude=True)
    next_versions: Optional[List['Document']] = Field(default_factory=list, exclude=True)
    raw_topics: Optional[List['RawTopic']] = []
    document_topics: Optional[List['DocumentTopic']] = []
    raw_entities: Optional[List['RawEntity']] = []
    document_entities: Optional[List['DocumentEntity']] = []
    events: Optional[List] = []

    def compose_DocumentCreated_event(self, doc_comments) -> None:
        if doc_comments is not None:
            docx_comments = [DocxComment(*c) for c in doc_comments]
            self.events.append(events.DocumentCreated(
            document_id=self.id, 
            comments=[{
                'document_id': self.id,
                'reference_text': c.reference_text,
                'author': c.author,
                'comment_date': datetime.strptime(c.date, '%Y-%m-%dT%H:%M:%SZ'),
                'comment_text': c.comment_text} 
                      for c in docx_comments]))
        return None

    def __hash__(self):
        return hash((self.id, self.filepath, self.filename, self.version))

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            'Document': lambda v: v.dict(exclude={'next_versions', 'previous_versions', 'comments'})
        }

class Comment(BaseModel):
    id: int
    document_id: int
    author: str
    reference_text: str
    comment_text: str
    comment_date: datetime
    events: Optional[List] = []
    document: Optional[Document] = None

    def __hash__(self):
        return hash((self.id, self.document_id, self.author, self.comment_date))

    class Config:
        from_attributes = True

class RawTopic(BaseModel):
    id: int
    document_id: int
    topic_name: str
    topic_description: str
    topic_prevalence: int
    document: Optional[Document] = None

    def __hash__(self):
        return hash((self.id, self.document_id, self.topic_description))

    class Config:
        from_attributes = True

class Topic(BaseModel):
    id: int
    topic_name: str
    topic_description: str
    document_topics: Optional[List['DocumentTopic']] = []
    raw_topics: Optional[List['TopicRawTopic']] = []

    
    def __hash__(self):
        return hash((self.id, self.topic_description))

    class Config:
        from_attributes = True

class DocumentTopic(BaseModel):
    document_id: int
    topic_id: int
    document: Optional[Document] = None
    topic: Optional[Topic] = None

    
    def __hash__(self):
        return hash((self.topic_id, self.document_id))

    class Config:
        from_attributes = True

class TopicRawTopic(BaseModel):
    topic_id: int
    raw_topic_id: int
    topic: Optional[Topic] = None
    raw_topic: Optional[RawTopic] = None

    
    def __hash__(self):
        return hash((self.topic_id, self.raw_topic_id))

    class Config:
        from_attributes = True

class RawEntity(BaseModel):
    id: int
    document_id: int
    entity_name: str
    entity_description: str
    entity_prevalence: int
    document: Optional[Document] = None

    def __hash__(self):
        return hash((self.id, self.document_id, self.entity_description))

    class Config:
        from_attributes = True

class Entity(BaseModel):
    id: int
    entity_name: str
    entity_description: str
    document_entities: Optional[List['DocumentEntity']] = []
    raw_entities: Optional[List['EntityRawEntity']] = []

    
    def __hash__(self):
        return hash((self.id, self.entity_name, self.entity_description))

    class Config:
        from_attributes = True

class DocumentEntity(BaseModel):
    document_id: int
    entity_id: int
    document: Optional[Document] = None
    entity: Optional[Entity] = None

    
    def __hash__(self):
        return hash((self.entity_id, self.document_id))

    class Config:
        from_attributes = True

class EntityRawEntity(BaseModel):
    entity_id: int
    raw_entity_id: int
    entity: Optional[Entity] = None
    raw_entity: Optional[RawEntity] = None

    
    def __hash__(self):
        return hash((self.entity_id, self.raw_entity_id))

    class Config:
        from_attributes = True

class DocxComment(NamedTuple):
    reference_text: str
    author: str
    date: str
    comment_text: str
