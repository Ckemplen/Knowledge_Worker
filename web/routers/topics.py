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
async def get_topic_row_edit_form(
    request: Request, topic_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    topic = views.get_topic_by_id(uow=bus.uow, id=topic_id)
    return templates.TemplateResponse(
        "components/topic_row.html",
        {"request": request, "topic": topic},
        status_code=200,  # Retrieved successfully
    )
