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

app = FastAPI()
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/documents", response_class=HTMLResponse, tags=['documents'])
async def add_document(request: Request, document: UploadFile = Form(...), bus: messagebus.MessageBus = Depends(get_bus)):
    print(document.filename)
    # Check for valid PDF upload
    if document.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload a PDF.",
        )
    # Handle file upload
    try:
        # Create a directory for uploaded files if it doesn't exist
        upload_dir = "uploaded_documents"
        os.makedirs(upload_dir, exist_ok=True)

        # Save the uploaded file
        file_path = os.path.join(upload_dir, document.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(document.file, buffer)


    except Exception as e:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {e}",
        ) from e

    # Extract text using PyPDF2
    try:
        text = ""
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text: {e}",
        ) from e
    
    cmd = commands.CreateDocument(
        filepath = document.filename,
        filename = document.filename,
        text = text,
        created_by="CKEMPLEN",
        last_modified_by="CKEMPLEN",
        filetype = document.filename.split(".")[-1]
    )

    bus.handle(cmd)
    new_document = views.get_document_by_filename(bus.uow, document.filename)
    return templates.TemplateResponse(
        "components/document_row.html", {"document": new_document}
    )


@router.delete("/{document_id}", response_class=HTMLResponse, tags=['documents'])
async def delete_document(
    request: Request, document_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    cmd = commands.RemoveDocument(document_id)
    bus.handle(cmd)
    return ""  # Return empty string on success


@router.put("/{document_id}", response_class=HTMLResponse, tags=['documents'])
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


@router.get("/{document_id}/edit", response_class=HTMLResponse, tags=['documents'])
async def get_document_row_edit_form(
    request: Request, document_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    document = views.get_document_by_id(uow=bus.uow, id=document_id)
    return templates.TemplateResponse(
        "components/document_row_edit.html",
        {"request": request, "document": document},
        status_code=200 # Retrieved successfully
    )

@router.get("/{document_id}", response_class=HTMLResponse, tags=['documents'])
async def get_document_row(
    request: Request, document_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    document = views.get_document_by_id(uow=bus.uow, id=document_id)
    return templates.TemplateResponse(
        "components/document_row.html",
        {"request": request, "document": document},
        status_code=200 # Retrieved successfully
    )
