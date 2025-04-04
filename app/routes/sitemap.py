from fastapi import APIRouter, HTTPException, Depends,status
from sqlalchemy.orm import Session, joinedload 
from app.models.sitemap_models import SitemapGenerator, ProjectBrief, saveSitemap
from app.services.llm_service import get_llm_response, get_llm_response_without_fmt
import json
from app.entities.sitemap_entities import Sitemap
from app.entities.user_entities import User
from app.entities.project_entities import Project
from app.services.auth_service import get_current_user
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




@router.put("/save-sitemap/{project_id}")
async def update_project_sitemap(
    project_id: int,
    payload: saveSitemap,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logging.info(f"User {current_user.id} attempting to save sitemap for project ID: {project_id}")
    sitemap_record = None

    try:
        project =  db.query(Project).filter(Project.id == project_id).first()

        if not project:
            logging.warning(f"Save sitemap failed: Project ID {project_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        if not project:
            logging.warning(f"Authorization failed: User {current_user.id} tried to update sitemap for project {project_id} owned by {project.created_by}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this project's sitemap")
        
        current_active_sitemap = db.query(Sitemap).filter(
            Sitemap.project_id == project_id,
            Sitemap.is_active == True
        ).with_for_update().first()

        if current_active_sitemap:
            logging.info(f"Deactivating previous active sitemap (ID: {current_active_sitemap.id}) for project {project_id}")
            current_active_sitemap.is_active = False
            db.add(current_active_sitemap)

        if payload.sitemap_data is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is no changes happened to save")
        
        new_sitemap = Sitemap(
            project_id=project_id,
            project_description=payload.project_description,
            no_of_pages=payload.no_of_pages,
            sitemap_data=payload.sitemap_data,
            is_active=True,
            created_by=current_user.id,
            updated_by=current_user.id
        )

        db.add(new_sitemap)

        if payload.project_name is not None and payload.project_name.strip() != project.project_name:
             project.project_name = payload.project_name.strip()
             project.updated_by = current_user.id
             db.add(project)

        db.commit()

        db.refresh(new_sitemap)
        db.refresh(project)
        logging.info(f"Successfully saved new sitemap version (ID: {new_sitemap.id}) for project {project_id}")
        return {
            "message":"New sitemap version saved successfully",
            "project_id":project.id,
            "sitemap_id":new_sitemap.id, 
            "project_name":project.project_name
        }
    
    except HTTPException as http_exc:
        db.rollback()
        logging.error(f"HTTP error occurred: {http_exc.detail}", exc_info=True)
        raise http_exc
    
    except Exception as e:
        db.rollback()
        logging.error(f"Error saving sitemap for project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error saving sitemap version.")
