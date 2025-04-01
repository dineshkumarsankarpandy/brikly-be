import logging
from fastapi import Request, HTTPException
from app.services.auth_service import decode_access_token
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings
from fastapi.responses import JSONResponse
from app.core.config import logging

logging.basicConfig(
    level=logging.INFO if settings.ENV == "development" else logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


        




def get_environment():
    return settings.ENV
