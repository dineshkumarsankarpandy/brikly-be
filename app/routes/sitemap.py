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
