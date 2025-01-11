from core.service_layer import unit_of_work
from sqlalchemy import text
import domain.model


def get_all_documents(uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.documents.list()

    return results


def get_all_stakeholders(uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.stakeholders.list()
    return results


def get_all_topics(uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.topics.list()

    return results


def get_all_entities(uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.entities.list()

    return results

def get_entity_by_id(uow: unit_of_work.SqlAlchemyUnitOfWork, id: int):
    with uow:
        result = uow.entities.get(reference=id)
    return result

def get_document_by_filename(uow: unit_of_work.SqlAlchemyUnitOfWork, filename: str):
    with uow:
        result = uow.session.execute(
            text(
                """
            SELECT * FROM Documents 
            WHERE filename = :filename 
            ORDER BY version DESC 
            LIMIT 1;
            """,
                {"filename": filename},
            )
        ).fetchone()
    return domain.model.Document(result) if result else None

def get_document_by_id(uow: unit_of_work.SqlAlchemyUnitOfWork, id: int):
    with uow:
        result = uow.documents.get(reference=id)
    return result

def get_stakeholder_by_name(uow: unit_of_work.SqlAlchemyUnitOfWork, name: str):
    with uow:
        result = uow.stakeholders.get_stakeholder_by_name(name=name)
    return result

def get_stakeholder_by_id(uow: unit_of_work.SqlAlchemyUnitOfWork, id: int):
    with uow:
        result = uow.stakeholders.get(reference=id)
    return result

def get_entity_documents(uow: unit_of_work.SqlAlchemyUnitOfWork):
    entity_documents = {}
    with uow:
        links = uow.session.execute(
            text(
                """
                SELECT document_id, entity_id FROM DocumentEntities 
                """
            )
        ).all()

        for document_id, entity_id in links:
            entity_documents[entity_id] = []
        for document_id, entity_id in links:
            entity_documents[entity_id].append(document_id)

        return entity_documents