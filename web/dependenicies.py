from core.adapters import llm_connectors
from core.service_layer import unit_of_work
from core import bootstrap


def get_bus():
    return bootstrap.bootstrap(
        uow=unit_of_work.SqlAlchemyUnitOfWork(),
        document_analysis_connector=llm_connectors.DocumentAnalysisConnector(),
        canonical_entity_consolidation_connector=llm_connectors.CanonicalEntityConsolidationConnector(),
    )
