import inspect
from core.adapters import llm_connectors

from core.service_layer import handlers, messagebus, unit_of_work


def bootstrap(
    uow: unit_of_work.AbstractUnitOfWork,
    document_analysis_connector: llm_connectors.DocumentAnalysisConnector,
    canonical_entity_consolidation_connector: llm_connectors.CanonicalEntityConsolidationConnector,
) -> messagebus.MessageBus:
    dependencies = {
        "uow": uow,
        "document_analysis_connector": document_analysis_connector,
        "canonical_entity_consolidation_connector": canonical_entity_consolidation_connector,
    }

    injected_event_handlers = {
        event_type: [
            (handler_name, inject_dependencies(handler, dependencies))
            for handler_name, handler in event_handlers
        ]
        for event_type, event_handlers in handlers.EVENT_HANDLERS.items()
    }

    injected_command_handlers = {
        command_type: (handler_name, inject_dependencies(handler, dependencies))
        for command_type, (handler_name, handler) in handlers.COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency for name, dependency in dependencies.items() if name in params
    }
    return lambda message: handler(message, **deps)
