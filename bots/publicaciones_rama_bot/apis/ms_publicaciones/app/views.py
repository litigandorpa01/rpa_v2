from . import app

from fastapi import APIRouter

from app.routes import publicaciones_routes


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(publicaciones_routes.router,tags=["Publicaciones"])

app.include_router(api_router)