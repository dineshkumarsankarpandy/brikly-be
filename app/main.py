# main.py

from fastapi import FastAPI
from app.routes import user_routes, project_routes, sitemap
from app.core.settings import settings
from app.core.config import setup_cors 

bearer_scheme_definition = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT", 
        "description": "Enter JWT Bearer token **only**",
    }
}

app = FastAPI(
    title=settings.APP_NAME,
    openapi_components={"securitySchemes": bearer_scheme_definition},
)


setup_cors(app)

app.include_router(user_routes.router) 

app.include_router(
    project_routes.router)
app.include_router(
    sitemap.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Sitemap Generator API"}