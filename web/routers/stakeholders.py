from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core import views
from core.service_layer import messagebus
from core.domain import commands

from ..dependenicies import get_bus


templates = Jinja2Templates(directory="web/templates")


router = APIRouter(
    prefix="/stakeholders",
    tags=["stakeholders"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/stakeholders", response_class=HTMLResponse)
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


@router.get("/{stakeholder_id}/edit", response_class=HTMLResponse)
async def get_stakeholder_row_edit_form(
    request: Request, stakeholder_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    stakeholder = views.get_stakeholder_by_id(uow=bus.uow, id=stakeholder_id)
    return templates.TemplateResponse(
        "components/stakeholder_row_edit.html",
        {"request": request, "stakeholder": stakeholder},
        status_code=200,  # Retrieved successfully
    )


@router.get("/{stakeholder_id}", response_class=HTMLResponse)
async def get_stakeholder_row(
    request: Request, stakeholder_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    stakeholder = views.get_stakeholder_by_id(uow=bus.uow, id=stakeholder_id)
    return templates.TemplateResponse(
        "components/stakeholder_row.html",
        {"request": request, "stakeholder": stakeholder},
        status_code=200,  # Retrieved successfully
    )


@router.put("/{stakeholder_id}", response_class=HTMLResponse)
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

@router.delete("/{stakeholder_id}", response_class=HTMLResponse)
async def delete_stakeholder(
    request: Request, stakeholder_id: int, bus: messagebus.MessageBus = Depends(get_bus)
):
    try:
        cmd = commands.DeleteStakeholder(id=stakeholder_id)
        bus.handle(message=cmd)
        # Return empty response which HTMX will remove
        return HTMLResponse("", status_code=200)
    except Exception as e:
        # Return error message that will be shown to user
        return templates.TemplateResponse(
            "components/error_message.html",
            {"request": request, "error_message": f"Failed to delete stakeholder: {str(e)}"},
            status_code=500
        )
