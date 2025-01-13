from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core import views
from core.service_layer import messagebus

from ..dependenicies import get_bus


templates = Jinja2Templates(directory="web/templates")


router = APIRouter(
    prefix="/topics",
    tags=["topics"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/{topic_id}", response_class=HTMLResponse)
async def get_topic_row(
    request: Request, 
    topic_id: int, 
    bus: messagebus.MessageBus = Depends(get_bus)
):
    topic = views.get_topic_by_id(uow=bus.uow, id=topic_id)
    return templates.TemplateResponse(
        "components/topic_row.html",
        {
            "request": request, 
            "topic": topic,
            "edit_mode": False
        },
        status_code=200,
    )

@router.get("/{topic_id}/edit", response_class=HTMLResponse)
async def get_topic_row_edit_form(
    request: Request, 
    topic_id: int, 
    bus: messagebus.MessageBus = Depends(get_bus)
):
    topic = views.get_topic_by_id(uow=bus.uow, id=topic_id)
    return templates.TemplateResponse(
        "components/topic_row.html",
        {
            "request": request, 
            "topic": topic,
            "edit_mode": True
        },
        status_code=200,
    )

@router.post("/", response_class=HTMLResponse)
async def create_topic(
    request: Request,
    topic_name: str,
    topic_description: str,
    bus: messagebus.MessageBus = Depends(get_bus)
):
    cmd = commands.CreateTopic(
        topic_name=topic_name,
        topic_description=topic_description
    )
    bus.handle(cmd)
    return RedirectResponse(url="/", status_code=303)

@router.put("/{topic_id}", response_class=HTMLResponse) 
async def update_topic(
    request: Request,
    topic_id: int,
    topic_name: str,
    topic_description: str,
    bus: messagebus.MessageBus = Depends(get_bus)
):
    cmd = commands.UpdateTopic(
        id=topic_id,
        topic_name=topic_name,
        topic_description=topic_description
    )
    bus.handle(cmd)
    return RedirectResponse(url="/", status_code=303)

@router.delete("/{topic_id}", response_class=HTMLResponse)
async def delete_topic(
    request: Request,
    topic_id: int,
    bus: messagebus.MessageBus = Depends(get_bus)
):
    cmd = commands.DeleteTopic(id=topic_id)
    bus.handle(cmd)
    return RedirectResponse(url="/", status_code=303)
