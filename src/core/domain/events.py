from dataclasses import dataclass
from typing import Optional, List, Dict
from core.adapters.llm_connectors import CanonicalEntityResponseItem


class Event:
    pass


@dataclass
class DocumentCreated(Event):
    document_id: int
    comments: Optional[List[Dict]]


@dataclass
class DocumentProcessed(Event):
    document_id: int


@dataclass
class CommentCreated(Event):
    comment_id: int
    document_id: int


@dataclass
class ExistingCanonicalEntityHallucination(Event):
    item: CanonicalEntityResponseItem
    entity_id: int
