from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Union
from datetime import datetime, timezone


class Command:
    pass


@dataclass(kw_only=True)
class CommandModifiedAudit(Command):
    last_modified_by: str = "ADMIN"
    last_modified_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )


@dataclass(kw_only=True)
class CommandCreatedAudit(CommandModifiedAudit):
    created_by: str = "ADMIN"
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


@dataclass(kw_only=True)
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


@dataclass(kw_only=True)
class ProcessDocument(CommandModifiedAudit):
    document_id: int


@dataclass(kw_only=True)
class UpdateDocumentSummary(CommandModifiedAudit):
    id: int
    summary: str


@dataclass(kw_only=True)
class ConsolidateCanonicalEntities(Command):
    """Pass in list of specific ids, or leave as None to review all."""

    entity_ids: Union[List[int], None]
    raw_entity_ids: Union[List[int], None]


@dataclass(kw_only=True)
class AddStakeholder(CommandCreatedAudit):
    stakeholder_name: str
    stakeholder_type: str
    stakeholder_description: str


@dataclass(kw_only=True)
class UpdateStakeholder(CommandCreatedAudit):
    id: int
    stakeholder_name: str
    stakeholder_type: str
    stakeholder_description: str


@dataclass(kw_only=True)
class AddEntity(CommandCreatedAudit):
    entity_name: str
    entity_description: str


@dataclass(kw_only=True)
class UpdateEntity(CommandModifiedAudit):
    id: int
    entity_name: str
    entity_description: str


@dataclass(kw_only=True)
class CreateTopic(CommandCreatedAudit):
    topic_name: str
    topic_description: str


@dataclass(kw_only=True)
class UpdateTopic(CommandModifiedAudit):
    id: int
    topic_name: str
    topic_description: str


@dataclass(kw_only=True)
class DeleteTopic(CommandModifiedAudit):
    id: int


@dataclass(kw_only=True)
class DeleteStakeholder(CommandModifiedAudit):
    id: int
