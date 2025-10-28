from fastapi import APIRouter
from lnbits.db import Database

db = Database("ext_nostrwallet")

nostrwallet_ext: APIRouter = APIRouter(
    prefix="/nostrwallet",
    tags=["nostrwallet"]
)

nostrwallet_static_files = [
    {
        "path": "/nostrwallet/static",
        "name": "nostrwallet_static",
    }
]


def nostrwallet_renderer():
    return {
        "name": "nostrwallet",
    }


from .views import *  # noqa: F401,F403
from .views_api import *  # noqa: F401,F403
