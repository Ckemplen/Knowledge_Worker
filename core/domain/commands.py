from dataclasses import dataclass, field, fields
from typing import Optional, List, Tuple, Union
from datetime import datetime, timezone


class Command:
    pass

class CommandModifiedAudit(Command):
    def __init__(self, last_modified_by="ADMIN", last_modified_at=None):
        self.last_modified_by = last_modified_by
        self.last_modified_at = last_modified_at or datetime.now(tz=timezone.utc)

class CommandCreatedAudit(CommandModifiedAudit):
    def __init__(self, created_by="ADMIN", created_at=None, **kwargs):
        super().__init__(**kwargs)
        self.created_by = created_by
        self.created_at = created_at or datetime.now(tz=timezone.utc)

@dataclass
class CreateDocument(CommandCreatedAudit):  
    filepath: str
    filename: str
    text: str
    processed_at: datetime = datetime.now(tz=timezone.utc)
    doc_comments: Optional[List[Tuple]] = None
    revision: Optional[int] = 0
    filetype: Optional[str] = None
    version_comment: Optional[str] = None
    html_text: Optional[str] = None
    version: Optional[int] = 1
    previous_version_id: Optional[int] = None


@dataclass
class ProcessDocument(CommandModifiedAudit):
    document_id: int


@dataclass
class UpdateDocumentSummary(CommandModifiedAudit):
    id: int
    summary: str


@dataclass
class ConsolidateCanonicalEntities(Command):
    """Pass in list of specific ids, or leave as None to review all."""

    entity_ids: Union[List[int], None]
    raw_entity_ids: Union[List[int], None]


@dataclass
class AddStakeholder(CommandCreatedAudit):
    stakeholder_name: str
    stakeholder_type: str
    stakeholder_description: str


@dataclass
class UpdateStakeholder(CommandModifiedAudit):
    id: int
    stakeholder_name: str
    stakeholder_type: str
    stakeholder_description: str


@dataclass
class UpdateEntity(CommandModifiedAudit):
    id: int
    entity_name: str
    entity_description: str


@dataclass
class CreateTopic(CommandCreatedAudit):
    topic_name: str
    topic_description: str


@dataclass
class UpdateTopic(CommandModifiedAudit):
    id: int
    topic_name: str
    topic_description: str


@dataclass
class DeleteTopic(CommandModifiedAudit):
    id: int


@dataclass
class DeleteStakeholder(CommandModifiedAudit):
    id: int
