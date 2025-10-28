from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

from . import nostrwallet_ext, nostrwallet_renderer

templates = template_renderer("nostrwallet")


@nostrwallet_ext.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user: User = Depends(check_user_exists),
):
    """Main page for Nostr Wallet Connect"""
    return templates.TemplateResponse(
        "nostrwallet/index.html",
        {
            "request": request,
            "user": user.dict(),
        },
    )
