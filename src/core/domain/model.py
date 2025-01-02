from pydantic import BaseModel
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
    comments: Optional[List['Comment']] = []
    previous_versions: Optional[List['Document']] = []
    events: Optional[List] = []
    #next_versions: Optional[List['Document']] = []

    def compose_DocumentCreated_event(self, doc_comments) -> None:
        if doc_comments is not None:
            docx_comments = [DocxComment(*c) for c in doc_comments]
            self.events.append(events.DocumentCreated(
            document_id=self.id, 
            comments=[{
                'doc_id': self.id,
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

class Comment(BaseModel):
    id: int
    document_id: int
    author: str
    reference_text: str
    comment_text: str
    comment_date: datetime
    events: Optional[List] = []
    #document: Optional[Document] = None

    
    def __hash__(self):
        return hash((self.id, self.document_id, self.author, self.comment_date))

    class Config:
        from_attributes = True

class DocxComment(NamedTuple):
    reference_text: str
    author: str
    date: str
    comment_text: str
