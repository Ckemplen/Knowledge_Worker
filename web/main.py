from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.core import bootstrap
from src.core.adapters import llm_connectors
from src.core.service_layer import messagebus, unit_of_work
from src.core.domain import commands
from src.core import views

app = FastAPI()
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

def get_bus():
    return bootstrap.bootstrap(
        uow=unit_of_work.SqlAlchemyUnitOfWork(),
        document_analysis_connector=llm_connectors.DocumentAnalysisConnector(),
        canonical_entity_consolidation_connector=llm_connectors.CanonicalEntityConsolidationConnector()
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, bus: messagebus.MessageBus = Depends(get_bus)):
    documents = views.get_all_documents(bus.uow)
    topics = views.get_all_topics(bus.uow)
    entities = views.get_all_entities(bus.uow)
    return templates.TemplateResponse("index.html", {"request": request, "documents": documents, "topics": topics, "entities": entities})


@app.post("/documents", response_class=HTMLResponse)
async def add_document(request: Request, bus: messagebus.MessageBus = Depends(get_bus)):
    form_data = await request.form()
    cmd = commands.AddDocument(form_data["filename"], form_data["filepath"])
    bus.handle(cmd)
    new_document = views.get_document_by_filename(bus.uow, form_data["filename"])
    return templates.TemplateResponse("components/document_row.html", {"document": new_document})

@app.delete("/documents/{document_id}", response_class=HTMLResponse)
async def delete_document(request: Request, document_id: int, bus: messagebus.MessageBus = Depends(get_bus)):
    cmd = commands.RemoveDocument(document_id)
    bus.handle(cmd)
    return "" # Return empty string on success

@app.put("/documents/{document_id}", response_class=HTMLResponse)
async def update_document(request: Request, document_id: int, bus: messagebus.MessageBus = Depends(get_bus)):
    form_data = await request.form()
    cmd = commands.UpdateDocument(document_id, form_data["filename"], form_data["filepath"])
    bus.handle(cmd)
    updated_document = views.get_document_by_id(bus.uow, document_id)
    return templates.TemplateResponse("components/document_row.html", {"document": updated_document})

@app.post("/stakeholders", response_class=HTMLResponse)
async def add_document(request: Request, bus: messagebus.MessageBus = Depends(get_bus)):
    form_data = await request.form()
    print(form_data)
    cmd = commands.AddStakeholder(form_data["stakeholder_name"], form_data["stakeholder_type"])
    print(f"Message type: {type(cmd)}")
    bus.handle(message=cmd)
    new_stakeholder = views.get_stakeholder_by_name(bus.uow, form_data["stakeholder_name"])
    return templates.TemplateResponse("components/stakeholder_row.html", {"document": new_stakeholder})
