from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from lnbits.db import Database

db = Database("ext_satsball")
templates = Jinja2Templates(directory="satsball/templates")

satsball_ext: APIRouter = APIRouter(prefix="/satsball", tags=["satsball"])

satsball_static_files = [
    {
        "path": "/satsball/static",
        "name": "satsball_static",
    }
]

from . import views, views_api  # noqa
from .migrations import m001_initial  # noqa