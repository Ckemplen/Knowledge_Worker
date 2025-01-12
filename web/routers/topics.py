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
    prefix="/topics",
    tags=["topics"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/{topic_id}", response_class=HTMLResponse)
async def get_topic_row_edit_form(
    request: Request, entity_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    topic = views.get_topic_by_id(uow=bus.uow, id=topic_id)
    return templates.TemplateResponse(
        "components/topic_row.html",
        {"request": request, "topic": topic},
        status_code=200 # Retrieved successfully
    )
