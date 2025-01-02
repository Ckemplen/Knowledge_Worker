from dataclasses import dataclass, make_dataclass
from typing import Optional, List, Tuple
from datetime import datetime

# from schema import And, Schema, Use
# import json


# def command(name, **fields):
#     schema = Schema(And(Use(json.loads), fields), ignore_extra_keys=True)
#     cls = make_dataclass(name, fields.keys())
#     cls.from_json = lambda s: cls(**schema.validate(s))
#     return cls

# def greater_than_zero(x):
#     return x > 0

# quantity = And(Use(int), greater_than_zero)

class Command:
    pass

# CreateDocument: Command = command(
#     'CreateDocument',
#     filepath=str,
#     filename=str,
#     text=str,
#     html_text=Optional[str],
#     last_modified_at=datetime,
#     created_at=datetime,
#     processed_at=datetime,
#     created_by=str,
#     last_modified_by=str,
#     revision=Optional[int],
#     filetype=Optional[str],
#     version_comment=Optional[str],
#     doc_comments=Optional[List[Tuple]]
# )

# ProcessDocument: Command = command(
#     'ProcessDocument',
#     document_id=int
#     )



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
    