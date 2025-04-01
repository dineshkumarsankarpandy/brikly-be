from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.sitemap_models import SitemapGenerator, ProjectBrief, SaveSitemapRequest
from app.services.llm_service import get_llm_response, get_llm_response_without_fmt
import json
from app.entities.sitemap_entities import Sitemap
from app.core.db_setup import get_db
from app.core.config import logging

router = APIRouter(prefix="/sitemap", tags=["Sitemap"])


@router.post("/generate")
async def generate_sitemap_generator(data: SitemapGenerator):
    prompt = """ 
    You provide assistance with project brief,
    You understand the business requirement and you are highly skillful to rewrite the business description 
    that is well detailed and crystal clear to be understood by everyone.
    """

    response = get_llm_response(
        user_prompt=f"write a project brief make it understandable {data.business_name}, {data.business_description}",
        system_prompt=prompt,
        response_format=ProjectBrief,
    )

    json_project = response.model_dump_json()
    project_brief = json.loads(json_project)

    sitemap_prompt = """
    Tasks:
    sitemap: Please write a list of 4 pages for the company's website as a comma-separated sequence.
    sitemap : Home, About Us, Blogs > Blog Post, Services > Service 1.

    Pages : Write the sitemap for the website. Include navbar and footer.
    Add a Description for the section.

    Give them in a JSON format: {
        "Sitemap": "",
        "Pages": [
            {
                "pageId": "",
                "pageName": "",
                "sections": [
                    {
                        "sectionName": "",
                        "section_description": "",
                        "section_outline": ""
                    }
                ]
            }
        ]
    }

    Strictly avoid extra text or any unrelated response.
    """

    response = get_llm_response_without_fmt(
        user_prompt=f"""
        Complete all the given tasks for the business: {data.business_name}.
        Write a project brief.
        Generate the sitemap.
        {sitemap_prompt}
        """
    )

    try:
        formatted_response = response.replace("```json", "").replace("```", "").strip()
        json_loads = json.loads(formatted_response)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, detail="Failed to parse JSON response from AI model"
        )

    return {"sitemap": json_loads, "project_brief": project_brief}


@router.post("/save-projects")
async def save_project_details(data: SaveSitemapRequest, db: Session = Depends(get_db)):
    try:
        new_project = Sitemap(
            project_name=data.project_name,
            project_description=data.project_description,
            no_of_pages=data.no_of_pages or 0,
            sitemap_data=data.sitemap_data or {},
        )

        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return {"message": "sitemap saved successfully", "status": True}
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/get-projects")
async def get_all_projects(db: Session = Depends(get_db)):
    try:
        project = db.query(
            Sitemap.id, Sitemap.project_name, Sitemap.created_at, Sitemap.updated_at
        ).all()
        if not project:
            return {"status": False, "message": "No projects found", "data": []}

        return {
            "data": [
                {
                    "id": s.id,
                    "project_name": s.project_name,
                    "updated_at": s.updated_at,
                    "created_at": s.created_at,
                }
                for s in project
            ]
        }

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/get-projects/{id}")
async def get_project_by_id(id: int, db: Session = Depends(get_db)):
    try:
        project = db.query(Sitemap).filter(Sitemap.id == id).first()

        if not project:
            logging.error(f"Project with ID :{id} not found")
            raise HTTPException(status_code=404, detail="Project not found")

        return {
            "id": project.id,
            "project_name": project.project_name,
            "project_description": project.project_description,
            "sitemap_data": project.sitemap_data,
        }

    except Exception:
        logging.error("unexpected error.")
        raise HTTPException(status_code=500, detail="Internal server error")
            