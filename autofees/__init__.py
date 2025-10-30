from fastapi import APIRouter
from lnbits.db import Database

db = Database("ext_autofees")

autofees_ext: APIRouter = APIRouter(
    prefix="/autofees",
    tags=["autofees"]
)

autofees_static_files = [
    {
        "path": "/autofees/static",
        "name": "autofees_static",
    }
]


def autofees_renderer():
    return {
        "name": "autofees",
    }


from .views import *  # noqa: F401,F403
from .views_api import *  # noqa: F401,F403
