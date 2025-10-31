from fastapi import Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists

from . import satsball_ext, templates
from .crud import get_stacks, get_stack

@satsball_ext.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    stacks = await get_stacks()
    return templates.TemplateResponse(
        "satsball/index.html",
        {
            "request": request,
            "user": user.dict(),
            "stacks": [stack.dict() for stack in stacks]
        }
    )

@satsball_ext.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, user: User = Depends(check_user_exists)):
    stacks = await get_stacks(enabled_only=False)
    return templates.TemplateResponse(
        "satsball/admin.html",
        {
            "request": request,
            "user": user.dict(),
            "stacks": [stack.dict() for stack in stacks]
        }
    )

@satsball_ext.get("/admin/history/{stack_id}", response_class=HTMLResponse)
async def admin_history(request: Request, stack_id: str, user: User = Depends(check_user_exists)):
    # In a real implementation, this would fetch the win history for the stack
    history = []  # Placeholder for win history data
    stack = await get_stack(stack_id)  # Get stack details
    return templates.TemplateResponse(
        "satsball/history.html",
        {
            "request": request,
            "user": user.dict(),
            "history": history,
            "stack": stack.dict() if stack else None
        }
    )

@satsball_ext.get("/payment/{stack_id}", response_class=HTMLResponse)
async def payment(request: Request, stack_id: str, user: User = Depends(check_user_exists)):
    stack = await get_stack(stack_id)
    if not stack or not stack.enabled:
        return templates.TemplateResponse(
            "satsball/error.html",
            {
                "request": request,
                "error": "Stack not found or disabled"
            }
        )
    
    return templates.TemplateResponse(
        "satsball/payment.html",
        {
            "request": request,
            "user": user.dict(),
            "stack": stack.dict()
        }
    )