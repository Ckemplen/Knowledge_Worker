from fastapi import Request, Depends, APIRouter
from fastapi.templating import Jinja2Templates

from core import views
from core.service_layer import messagebus

from ..dependenicies import get_bus

from typing import Dict, List, Any


templates = Jinja2Templates(directory="web/templates")


router = APIRouter(
    prefix="/graphs",
    tags=["graphs"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/node_edge_graph_data", response_model=None)
async def get_node_edge_graph_data(
    request: Request, bus: messagebus.MessageBus = Depends(get_bus)
) -> Dict[str, List[Dict[str, Any]]]:
    documents = views.get_all_documents(bus.uow)
    topics = views.get_all_topics(bus.uow)
    entities = views.get_all_entities(bus.uow)
    stakeholders = views.get_all_stakeholders(bus.uow)

    nodes = []
    edges = []
    node_degrees = {}

    # Add documents as nodes
    for document in documents:
        node_id = f"document-{document.id}"
        nodes.append(
            {
                "id": node_id,
                "name": node_id,
                "label": document.filename,
                "group": "document",
                "degree": 0,
            }
        )
        node_degrees[node_id] = 0

    # Add topics as nodes
    for topic in topics:
        node_id = f"topic-{topic.id}"
        nodes.append(
            {
                "id": node_id,
                "name": node_id,
                "label": topic.topic_name,
                "group": "topic",
                "degree": 0,
            }
        )
        node_degrees[node_id] = 0

    # Add entities as nodes
    for entity in entities:
        node_id = f"entity-{entity.id}"
        nodes.append(
            {
                "id": node_id,
                "name": node_id,
                "label": entity.entity_name,
                "group": "entity",
                "degree": 0,
            }
        )
        node_degrees[node_id] = 0

    # Add stakeholders as nodes
    for stakeholder in stakeholders:
        node_id = f"stakeholder-{stakeholder.id}"
        nodes.append(
            {
                "id": node_id,
                "name": node_id,
                "label": stakeholder.stakeholder_name,
                "group": "stakeholder",
                "degree": 0,
            }
        )
        node_degrees[node_id] = 0

    # Create edges based on relationships
    for document in documents:
        for entity in document.entities:
            source_id = f"document-{document.id}"
            target_id = f"entity-{entity.id}"
            edges.append(
                {
                    "source": source_id,
                    "target": target_id,
                }
            )
            node_degrees[source_id] += 1
            node_degrees[target_id] += 1

    for node in nodes:
        node["degree"] = node_degrees[node["id"]]

    return {"nodes": nodes, "edges": edges}
