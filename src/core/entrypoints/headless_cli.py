import os
import datetime
from docx2python import docx2python

from core.database import create_database
from core.service_layer.unit_of_work import SqlAlchemyUnitOfWork
from core.adapters.llm_connectors import DocumentAnalysisConnector, CanonicalEntityConsolidationConnector
import core.bootstrap

import core.domain.commands
import core.service_layer.messagebus

from core.config import DATABASE_PATH, FILE_LIST


def process_file_list(file_list_path):

    try:
        with open(file_list_path, "r") as f:
            file_paths = [line.strip().strip('"') for line in f]
    except FileNotFoundError:
        print(f"Error: File list not found at {file_list_path}")
        return

    for file_path in file_paths:
        if not os.path.exists(file_path):
            print("Warning: File not found: {file_path}")
            continue

        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_path)[1].lower()

        if file_type != ".docx":
            print(f"Skipping non-docx file: {file_path}")
            continue

        print(f"Parsing docx file to db: {file_path}")

        create_document_from_docx(file_path)


def create_document_from_docx(file_path):

    doc = docx2python(file_path)
    html_text = docx2python(file_path, html=True).text

    file_name = os.path.basename(file_path)

    create_new_document = core.domain.commands.CreateDocument(
        filepath=file_path,
        filename=file_name,
        filetype=".docx",
        text=doc.text,
        html_text=html_text,
        last_modified_at=datetime.datetime.strptime(doc.properties.get('modified'), '%Y-%m-%dT%H:%M:%SZ'),
        processed_at=datetime.datetime.now(),
        created_at=datetime.datetime.strptime(doc.properties.get('created'), '%Y-%m-%dT%H:%M:%SZ'),
        created_by=doc.properties.get('creator', 'CKEMPLEN'),
        last_modified_by=doc.properties.get('lastModifiedBy', 'CKEMPLEN'),
        revision=doc.properties.get('revision', 0),
        doc_comments=doc.comments,
    )

    bus.handle(message=create_new_document)


if __name__ == "__main__":
    
    bus = core.bootstrap.bootstrap(
        uow=SqlAlchemyUnitOfWork(), 
        document_analysis_connector=DocumentAnalysisConnector(),
        canonical_entity_consolidation_connector=CanonicalEntityConsolidationConnector()
        )

    create_database(DATABASE_PATH)

    process_file_list(FILE_LIST)
