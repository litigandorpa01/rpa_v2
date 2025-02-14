from . import app
from .routes import tyba_routes
from fastapi import APIRouter


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(tyba_routes.router,tags=["Tyba"])

app.include_router(api_router)