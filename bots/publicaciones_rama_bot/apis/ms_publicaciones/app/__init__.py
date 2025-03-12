import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import OracleDB

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
)

#Eventos Pool BD
@asynccontextmanager
async def lifespan(app: FastAPI):
    #On start
    await OracleDB.create_pool()
    yield
    #On shutdown
    await OracleDB.close_pool()
    
app = FastAPI(
    title="ms_publicaciones API Service",
    description=(
        "ms_publicaciones app"
    ),
    version="0.1.0",
    contact={
        "name": "Rpa Litigando Department",
        "email": "correog@gmail.com",
    },
    openapi_url="/api/v1/scraping/openapi.json", 
    docs_url="/api/v1/scraping/docs",  
    redoc_url="/api/v1/scraping/redoc",
    lifespan=lifespan  
)

from .views import *