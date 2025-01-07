# pylint: disable=no-self-use
from __future__ import annotations
from datetime import datetime
from typing import Set
from core import bootstrap
from core.domain import commands, model, events
from core.adapters import repository, llm_connectors
from core.service_layer import unit_of_work
from dataclasses import asdict


class FakeDocumentsRepository(repository.AbstractRepository):
    def __init__(self, documents):
        super().__init__()
        self._documents: Set[model.Document] = set(documents)

    def _add(self, document):
        return self.add(document)

    def _get(self, reference):
        return self.get(reference)

    def add(self, cmd):
        document = asdict(cmd)
        doc_comments = document.get("doc_comments")
        del document["doc_comments"]
        doc = model.Document(**document, id=len(self._documents) + 1, summary="")
        doc.compose_DocumentCreated_event(doc_comments)
        self._documents.add(doc)
        return doc

    def get(self, reference):
        return next((d for d in self._documents if d.id == reference), None)

    def _list(self):
        return self._documents

    def get_by_comment_id(self, reference):
        return next(
            (d for d in self._documents for c in d.comments if c.id == reference),
            None,
        )


class FakeCommentsRepository(repository.AbstractRepository):
    def __init__(self, comments):
        super().__init__()
        self._comments: Set[model.Comment] = set(comments)

    def _add(self, comment):
        return self.add(comment)

    def _get(self, reference):
        return self.get(reference)

    def add(self, comment):
        comment = model.Comment(**comment, id=len(self._comments) + 1)
        self._comments.add(comment)

    def get(self, reference):
        return next((c for c in self._comments if c.id == reference), None)

    def _list(self):
        return self._comments


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.documents = FakeDocumentsRepository([])
        self.comments = FakeCommentsRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def commit(self):
        self._commit()

    def rollback(self):
        pass


def bootstrap_test_app():
    return bootstrap.bootstrap(
        uow=FakeUnitOfWork(),
        document_analysis_connector=llm_connectors.FakeDocumentAnalysisConnector(),
        canonical_entity_consolidation_connector=None,
    )


class TestAddDocument:
    def test_for_new_document(self):
        bus = bootstrap_test_app()
        bus.handle(
            commands.CreateDocument(
                filepath="fake/file/path",
                filename="fake/file/path.docx",
                text="Example text",
                created_by="CKEMPLEN",
                last_modified_by="CKEMPLEN",
                last_modified_at=datetime.now(),
                created_at=datetime.now(),
                processed_at=datetime.now(),
            )
        )
        assert bus.uow.documents.get(reference=1) is not None
        assert bus.uow.committed

    def test_for_existing_document(self):
        bus = bootstrap_test_app()
        bus.handle(
            commands.CreateDocument(
                filepath="fake/file/path",
                filename="fake/file/path.docx",
                text="Example text",
                created_by="CKEMPLEN",
                last_modified_by="CKEMPLEN",
                last_modified_at=datetime.now(),
                created_at=datetime.now(),
                processed_at=datetime.now(),
            )
        )
        bus.handle(
            commands.CreateDocument(
                filepath="fake/file/path",
                filename="fake/file/path.docx",
                text="Example text",
                created_by="CKEMPLEN",
                last_modified_by="CKEMPLEN",
                last_modified_at=datetime.now(),
                created_at=datetime.now(),
                processed_at=datetime.now(),
            )
        )
        assert bus.uow.documents.get(reference=2).previous_version_id == 1
        assert bus.uow.documents.get(reference=2).version == 2

    def test_comments_added(self):
        doc_comments = [
            {
                "reference_text": "reference text 1",
                "author": "author name 1",
                "comment_date": "2024-12-31T14:24:01Z",
                "comment_text": "comment text 1",
                "document_id": 1,
            },
        ]
        bus = bootstrap_test_app()

        bus.handle(events.DocumentCreated(document_id=1, comments=doc_comments))

        assert bus.uow.comments.get(reference=1).author == "author name 1"
