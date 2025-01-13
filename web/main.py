from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from core import views
from core.service_layer import messagebus

from .routers import documents, stakeholders, entities, graphs, topics
from .dependenicies import get_bus


app = FastAPI()
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

app.include_router(documents.router)
app.include_router(stakeholders.router)
app.include_router(entities.router)
app.include_router(topics.router)
app.include_router(graphs.router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, bus: messagebus.MessageBus = Depends(get_bus)):
    documents = views.get_all_documents(bus.uow)
    topics = views.get_all_topics(bus.uow)
    entities = views.get_all_entities(bus.uow)
    stakeholders = views.get_all_stakeholders(bus.uow)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "documents": documents,
            "topics": topics,
            "entities": entities,
            "stakeholders": stakeholders,
        },
    )
