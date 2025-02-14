from fastapi import FastAPI

import logging

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
)

app = FastAPI(
    title="ms_tyba API Service",
    description=(
        "ms_tyba app"
    ),
    version="0.1.0",
    contact={
        "name": "Rpa Department Litigando",
        "email": "correog@gmail.com",
    },
    openapi_url="/api/v1/scraping/openapi.json", 
    docs_url="/api/v1/scraping/docs",  
    redoc_url="/api/v1/scraping/redoc",  
)

from .views import *