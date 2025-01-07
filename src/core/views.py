from core.service_layer import unit_of_work
from sqlalchemy import text


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
    return dict(result) if result else None


def get_stakeholder_by_name(uow: unit_of_work.SqlAlchemyUnitOfWork, name: str):
    with uow:
        result = uow.stakeholders.get_stakeholder_by_name(name=name)
    return result
