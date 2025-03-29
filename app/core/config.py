import logging
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings


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
