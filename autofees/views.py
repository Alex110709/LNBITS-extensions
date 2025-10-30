from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

from . import autofees_ext

templates = template_renderer("autofees")


@autofees_ext.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user: User = Depends(check_user_exists),
):
    """Main page for Auto Channel Fees"""
    return templates.TemplateResponse(
        "autofees/index.html",
        {
            "request": request,
            "user": user.dict(),
        },
    )
