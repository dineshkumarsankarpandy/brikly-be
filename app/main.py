from fastapi import FastAPI
from app.routes import sitemap
from app.core.settings import settings
from app.core.config import setup_cors

app = FastAPI(title=settings.APP_NAME)


setup_cors(app)

# Include all route modules
app.include_router(sitemap.router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Sitemap Generator API"}

