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

    
    sectionCategoryCsv = """
    0|Navbar
    1|Hero Header Section
    2|Header Section
    3|Portfolio Item Header Section
    4|Project Item Header Section
    5|Portfolio Item Body Section
    6|Project Item Body Section
    7|Portfolio List Section
    8|Project List Section
    9|Blog Post Header Section
    10|Resource Item Header Section
    11|Case Study Header Section
    12|Press Article Header Section
    13|Update Item Header Section
    14|Event Item Header Section
    15|Blog Post Body Section
    16|Resource Item Body Section
    17|Case Study Body Section
    18|Documentation Body Section
    19|Press Release Body Section
    20|Legal Page Body Section
    21|Update Item Body Section
    22|Event Item Body Section
    23|Event Schedule Section
    24|Course Item Body Section
    25|Featured Blog List Header Section
    26|Featured Resources List Header Section
    27|Featured Case Study List Header Section
    28|Featured Press List Header Section
    29|Featured Updates List Header Section
    30|Featured Events List Header Section
    31|Featured Courses List Header Section
    32|Blog List Section
    33|Resources List Section
    34|Case Study List Section
    35|Press List Section
    36|Updates List Section
    37|Events List Section
    38|Courses List Section
    39|Feature Section
    40|Features List Section
    41|Benefits Section
    42|How It Works Section
    43|Services Section
    44|About Section
    45|Stats Section
    46|Ecommerce Product Section
    47|Timeline Section
    48|Ecommerce Product Header Section
    49|Course Item Header Section
    50|Ecommerce Products List Section
    51|Testimonial Section
    52|Reviews Section
    53|Pricing Section
    54|Pricing Comparison Section
    55|CTA Section
    56|CTA Form Section
    57|Newsletter Section
    58|Early Access Section
    59|Contact Section
    60|Contact Form Section
    61|Application Form Section
    62|Locations Section
    63|Gallery Section
    64|Announcement Banner
    65|Marquee Banner
    66|FAQ Section
    67|Team Section
    68|Logo List Section
    69|Award Logos List Section
    70|Customer Logos List Section
    71|Client Logos List Section
    72|Partner Logos List Section
    73|Job Listings Section
    74|Footer
    75|Comparison Section
    """
    
    output_json = '''
             {
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
'''

    sitemap_prompt = f"""
    Tasks:
    sitemap: Please write a {data.page} for the company's website as a comma-separated sequence.
    


    Pages : Write the sitemap for the website. Include navbar and footer.atleast pick more than 5 sections based on this {sectionCategoryCsv}
    Add a Description for the section.

    Give them in a JSON format:
            {output_json}

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
