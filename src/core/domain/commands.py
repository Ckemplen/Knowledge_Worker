from dataclasses import dataclass
from typing import Optional, List, Tuple, Union
from datetime import datetime


class Command:
    pass


@dataclass
class CreateDocument(Command):
    filepath: str
    filename: str
    text: str
    created_by: str
    last_modified_by: str
    last_modified_at: datetime = datetime.now()
    created_at: datetime = datetime.now()
    processed_at: datetime = datetime.now()
    doc_comments: Optional[List[Tuple]] = None
    revision: Optional[int] = 0
    filetype: Optional[str] = None
    version_comment: Optional[str] = None
    html_text: Optional[str] = None
    version: Optional[int] = 1
    previous_version_id: Optional[int] = None


@dataclass
class ProcessDocument(Command):
    document_id: int


@dataclass
class UpdateDocumentSummary(Command):
    id: int
    summary: str


@dataclass
class ConsolidateCanonicalEntities(Command):
    """Pass in list of specific ids, or leave as None to review all."""

    entity_ids: Union[List[int], None]
    raw_entity_ids: Union[List[int], None]


@dataclass
class AddStakeholder(Command):
    stakeholder_name: str
    stakeholder_type: str
    stakeholder_description: str


@dataclass
class UpdateStakeholder(Command):
    id: int
    stakeholder_name: str
    stakeholder_type: str
    stakeholder_description: str


@dataclass
class UpdateEntity(Command):
    id: int
    entity_name: str
    entity_description: str


@dataclass
class CreateTopic(Command):
    topic_name: str
    topic_description: str


@dataclass
class UpdateTopic(Command):
    id: int
    topic_name: str
    topic_description: str


@dataclass
class DeleteTopic(Command):
    id: int


@dataclass
class DeleteStakeholder(Command):
    id: int
