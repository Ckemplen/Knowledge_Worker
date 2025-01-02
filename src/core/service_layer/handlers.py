import core.domain.commands as commands
import core.domain.events as events
from core.domain.model import Document

import core.service_layer.unit_of_work as uow

from dataclasses import asdict
from typing import List, Tuple


def add_new_document(
        cmd: commands.CreateDocument, 
        uow: uow.AbstractUnitOfWork,
        ) -> Document:
    
    with uow:

        sorted_documents = sorted(uow.documents.list(), key=lambda d: d.version, reverse=True)
        existing_doc = next((d for d in sorted_documents if d.filepath == cmd.filepath), None)        
        if existing_doc is not None:
            cmd.version = existing_doc.version + 1
            cmd.previous_version_id = existing_doc.id

        new_doc = uow.documents.add(cmd)

        uow.collect_new_events()

        uow.commit()  # Commit the transaction

        return new_doc
    
def process_document(
        cmd: commands.ProcessDocument,
        uow: uow.AbstractUnitOfWork
):
    doc = uow.documents.get(reference=cmd.document_id)
    pass

def log_document_creation(*args, **kwargs):
    print("Document created 🥳")

def add_document_comments(
        event: events.DocumentCreated,
        uow: uow.AbstractUnitOfWork,
):
    with uow:
        for comment in event.comments:
            try:
                added_comment = uow.comments.add(comment)
                
                new_comment_event = events.CommentCreated(comment_id=added_comment.id, document_id=event.document_id)

                uow.collect_new_event(new_comment_event)

            except Exception as e:
                print(e)
                uow.rollback()
            finally:
                uow.commit()



EVENT_HANDLERS = {
   events.DocumentCreated: [add_document_comments, log_document_creation],
   events.CommentCreated: [],
   # events.DocumentProcessed: [],
}

COMMAND_HANDLERS = {
    commands.CreateDocument: add_new_document,
    commands.ProcessDocument: process_document,
}