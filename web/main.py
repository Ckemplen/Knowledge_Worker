from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from core import bootstrap, views
from core.adapters import llm_connectors
from core.service_layer import messagebus, unit_of_work
from core.domain import commands


app = FastAPI()
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


def get_bus():
    return bootstrap.bootstrap(
        uow=unit_of_work.SqlAlchemyUnitOfWork(),
        document_analysis_connector=llm_connectors.DocumentAnalysisConnector(),
        canonical_entity_consolidation_connector=llm_connectors.CanonicalEntityConsolidationConnector(),
    )


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


@app.get("/document_details/{document_id}", response_class=HTMLResponse)
async def document_details(
    request: Request, document_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    document = bus.uow.documents.get(reference=document_id)
    return templates.TemplateResponse(
        "components/document_row.html", {"document": document}
    )


@app.post("/documents", response_class=HTMLResponse)
async def add_document(request: Request, bus: messagebus.MessageBus = Depends(get_bus)):
    form_data = await request.form()
    cmd = commands.AddDocument(form_data["filename"], form_data["filepath"])
    bus.handle(cmd)
    new_document = views.get_document_by_filename(bus.uow, form_data["filename"])
    return templates.TemplateResponse(
        "components/document_row.html", {"document": new_document}
    )


@app.delete("/documents/{document_id}", response_class=HTMLResponse)
async def delete_document(
    request: Request, document_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    cmd = commands.RemoveDocument(document_id)
    bus.handle(cmd)
    return ""  # Return empty string on success


@app.put("/documents/{document_id}", response_class=HTMLResponse)
async def update_document(
    request: Request, document_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    form_data = await request.form()
    cmd = commands.UpdateDocumentSummary(
        id=document_id, 
        summary=form_data["summary"]
    )
    bus.handle(cmd)
    updated_document = views.get_document_by_id(bus.uow, document_id)
    return templates.TemplateResponse(
        "components/document_row.html", 
        {"request": request, 
         "document": updated_document},
         status_code=200
    )



@app.get("/documents/{document_id}/edit", response_class=HTMLResponse)
async def get_document_row_edit_form(
    request: Request, document_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    document = views.get_document_by_id(uow=bus.uow, id=document_id)
    return templates.TemplateResponse(
        "components/document_row_edit.html",
        {"request": request, "document": document},
        status_code=200 # Retrieved successfully
    )

@app.get("/documents/{document_id}", response_class=HTMLResponse)
async def get_document_row(
    request: Request, document_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    document = views.get_document_by_id(uow=bus.uow, id=document_id)
    return templates.TemplateResponse(
        "components/document_row.html",
        {"request": request, "document": document},
        status_code=200 # Retrieved successfully
    )

@app.get("/document-entity-options/{document_id}", response_class=HTMLResponse)
async def get_options(request: Request, document_id: int, bus: messagebus.MessageBus = Depends(get_bus)):
    document = views.get_document_by_id(uow=bus.uow, id=document_id)
    selected_ids = [entity.id for entity in document.entities]
    entities = views.get_all_entities(bus.uow)
    options_html = []
    for entity in entities:
        selected = "selected" if entity.id in selected_ids else ""
        options_html.append(f'<option value="{entity.id}" {selected}>{entity.entity_name}</option>')

    return templates.TemplateResponse("components/document_entity_options.html", {"request": request, "options_html": options_html})

@app.post("/stakeholders", response_class=HTMLResponse)
async def add_stakeholder(
    request: Request, bus: messagebus.MessageBus = Depends(get_bus)
):
    form_data = await request.form()
    cmd = commands.AddStakeholder(
        form_data["stakeholder_name"], form_data["stakeholder_type"]
    )
    bus.handle(message=cmd)
    new_stakeholder = views.get_stakeholder_by_name(
        uow=bus.uow, name=cmd.stakeholder_name
    )
    return templates.TemplateResponse(
        "components/stakeholder_row.html",
        {"request": request, "stakeholder": new_stakeholder},
        status_code=201,  # Created successfully
    )


@app.get("/stakeholders/{stakeholder_id}/edit", response_class=HTMLResponse)
async def get_stakeholder_row_edit_form(
    request: Request, stakeholder_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    stakeholder = views.get_stakeholder_by_id(uow=bus.uow, id=stakeholder_id)
    return templates.TemplateResponse(
        "components/stakeholder_row_edit.html",
        {"request": request, "stakeholder": stakeholder},
        status_code=200 # Retrieved successfully
    )

@app.get("/stakeholders/{stakeholder_id}", response_class=HTMLResponse)
async def get_stakeholder_row(
    request: Request, stakeholder_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    stakeholder = views.get_stakeholder_by_id(uow=bus.uow, id=stakeholder_id)
    return templates.TemplateResponse(
        "components/stakeholder_row.html",
        {"request": request, "stakeholder": stakeholder},
        status_code=200 # Retrieved successfully
    )

@app.put("/stakeholders/{stakeholder_id}", response_class=HTMLResponse)
async def update_stakeholder(
    request: Request, stakeholder_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    form_data = await request.form()
    print(form_data)
    cmd = commands.UpdateStakeholder(
        id=stakeholder_id,
        stakeholder_name=form_data["stakeholder_name"],
        stakeholder_type=form_data["stakeholder_type"],
    )
    bus.handle(message=cmd)
    new_stakeholder = views.get_stakeholder_by_name(
        uow=bus.uow, name=cmd.stakeholder_name
    )
    return templates.TemplateResponse(
        "components/stakeholder_row.html",
        {"request": request, "stakeholder": new_stakeholder},
        status_code=200,  # Updated successfully

    )


@app.get("/entities/{entity_id}/edit", response_class=HTMLResponse)
async def get_stakeholder_row_edit_form(
    request: Request, entity_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    entity = views.get_entity_by_id(uow=bus.uow, id=entity_id)
    return templates.TemplateResponse(
        "components/entity_row_edit.html",
        {"request": request, "entity": entity},
        status_code=200 # Retrieved successfully
    )

@app.get("/entities/{entity_id}", response_class=HTMLResponse)
async def get_entity_row_edit_form(
    request: Request, entity_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    entity = views.get_entity_by_id(uow=bus.uow, id=entity_id)
    return templates.TemplateResponse(
        "components/entity_row.html",
        {"request": request, "entity": entity},
        status_code=200 # Retrieved successfully
    )

@app.put("/entities/{entity_id}", response_class=HTMLResponse)
async def update_entity(
    request: Request, entity_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    form_data = await request.form()
    print(form_data)
    cmd = commands.UpdateEntity(
        id=entity_id,
        entity_name=form_data["entity_name"],
        entity_description=form_data["entity_description"],
    )
    bus.handle(message=cmd)
    new_entity = views.get_entity_by_id(
        uow=bus.uow, name=cmd.id
    )
    return templates.TemplateResponse(
        "components/entity_row.html",
        {"request": request, "entity": new_entity},
        status_code=200,  # Updated successfully

    )
