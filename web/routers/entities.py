from fastapi import FastAPI, Request, Depends, UploadFile, HTTPException, status, Form, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from core import bootstrap, views
from core.adapters import llm_connectors
from core.service_layer import messagebus, unit_of_work
from core.domain import commands

from ..dependenicies import get_bus

from typing import Dict, Union, List, Any

import pypdf as PyPDF2
import os
import shutil
from pathlib import Path


templates = Jinja2Templates(directory="web/templates")


router = APIRouter(
    prefix="/entities",
    tags=["entities"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/{entity_id}/edit", response_class=HTMLResponse)
async def get_stakeholder_row_edit_form(
    request: Request, entity_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    entity = views.get_entity_by_id(uow=bus.uow, id=entity_id)
    return templates.TemplateResponse(
        "components/entity_row_edit.html",
        {"request": request, "entity": entity},
        status_code=200 # Retrieved successfully
    )

@router.get("/{entity_id}", response_class=HTMLResponse)
async def get_entity_row_edit_form(
    request: Request, entity_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    entity = views.get_entity_by_id(uow=bus.uow, id=entity_id)
    return templates.TemplateResponse(
        "components/entity_row.html",
        {"request": request, "entity": entity},
        status_code=200 # Retrieved successfully
    )

@router.put("/{entity_id}", response_class=HTMLResponse)
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
