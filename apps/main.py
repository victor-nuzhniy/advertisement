"""Main FastAPI module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import Settings
from tags_metadata import metadata

app = FastAPI(openapi_tags=metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.CORS_ALLOW_ORIGINS,
    allow_credentials=Settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=Settings.CORS_ALLOW_METHODS,
    allow_headers=Settings.CORS_ALLOW_HEADERS,
)
