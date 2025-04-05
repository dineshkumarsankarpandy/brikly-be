from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import Dict,Tuple, List
import asyncio
from app.core.config import logging
# from app.services.llm_service import get_llm_response,get_llm_response_without_fmt
from app.services.geminillm_service import gemini_llm_call
from app.entities.project_entities import Project
from app.entities.sitemap_entities import Sitemap
from app.entities.user_entities import User
from app.core.db_setup import get_db
from app.services.auth_service import get_current_user
from app.models.website_models import (SectionData,
                                       PageData, 
                                       CreateWebsiteRequest, 
                                       WebsiteResponse, 
                                       SitemapStructure,
                                       SectionHtmlResponse,
                                       MultiPageWebsiteResponse)



router = APIRouter(prefix="/website", tags=["Website"])


async def generate_section_html(
    section: SectionData,
    page: PageData,
    project_context: Dict 
) -> Tuple[str, str, str]: 
    try:
        logging.info(f"Generating HTML for section '{section.sectionName}' on page '{page.pageName}'")

        system_prompt = f"""
        You are an expert frontend developer creating semantic HTML, potentially using Tailwind CSS.
        Generate the HTML code *only* for the website section described below.
        Wrap the output in a '<section id="section-{page.id }-{section.id}">' tag.
        Use placeholder images (e.g., https://via.placeholder.com/600x400) if needed.
        Do not include <html>, <head>, or <body> tags. Just the <section>...</section>.
        """

        user_prompt = f"""
        Project Context:
        Business Name: {project_context.get('business_name', 'N/A')}
        Project Description: {project_context.get('project_description', 'N/A')}

        Page Name: {page.pageName}

        Section Details:
        Section ID: {section.id}
        Section Name: {section.sectionName}
        Section Description: {section.section_description}
        # Include other details if relevant, like section_outline

        Generate the HTML code for this specific section now.
        """
        # --- Call your LLM function ---
        html_content =  gemini_llm_call(
            system_instruction=system_prompt,
            user_input=user_prompt,
           
        )
        # If response_format=SectionHtmlResponse was used:
        # if isinstance(html_content, SectionHtmlResponse):
        #    html_content = html_content.html_code
        # elif not isinstance(html_content, str): 
        #     raise ValueError("LLM returned unexpected format for section HTML")

        if not html_content or not isinstance(html_content, str):
             logging.error(f"Failed to generate HTML for section {section.id} on page {page.id}: Empty or invalid response.")
             return (str(page.id), str(section.id), f"<section id='section-{page.id}-{section.id}' class='bg-red-100 text-red-700 p-4'>Error generating content for '{section.sectionName}'.</section>")

        logging.info(f"Successfully generated HTML for section {section.id} on page {page.id}")
        return (str(page.id), str(section.id), html_content.strip())

    except Exception as e:
        logging.error(f"Error generating HTML for section {section.id} on page {page.id}: {e}", exc_info=True)
        return (str(page.id), str(section.id), f"<section id='section-{page.id}-{section.id}' class='bg-red-100 text-red-700 p-4'>Error generating content for '{section.sectionName}': {e}</section>")




@router.post("/create-website", response_model=MultiPageWebsiteResponse)
async def create_website(
    data: CreateWebsiteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sitemap_id_from_request = data.project_id
    try:
        # --- Verify Ownership and Fetch Data ---
        sitemap_db_entry = db.query(Sitemap)\
            .options(joinedload(Sitemap.project))\
            .join(Sitemap.project) \
            .filter(Sitemap.id == sitemap_id_from_request) \
            .filter(Project.created_by == current_user.id) \
            .first()

        # --- Correct Check for Existence and Permissions ---
        if not sitemap_db_entry:
            exists = db.query(Sitemap.id).filter(Sitemap.id == sitemap_id_from_request).first()
            if not exists:
                 raise HTTPException(
                     status_code=status.HTTP_404_NOT_FOUND,
                     detail=f"Sitemap with ID {sitemap_id_from_request} not found."
                 )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access the project associated with this sitemap."
                )

        # --- Validate Incoming Sitemap Structure ---
        sitemap: SitemapStructure = data.sitemap
        if not sitemap or not sitemap.Pages:
             raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                 detail="Sitemap data is missing or empty in the request payload.")

        actual_project_id = sitemap_db_entry.project_id 
        logging.info(f"Starting multi-page website generation for sitemap {sitemap_id_from_request} (Project ID: {actual_project_id}) by user {current_user.id}")

        tasks = []
        page_section_map: Dict[str, List[str]] = {}

        project_context = {
            "business_name": data.business_name or sitemap_db_entry.project.project_name, # From loaded project
            "project_description": data.project_description or sitemap_db_entry.project_description # From sitemap record
        }

        valid_pages_for_gen = [] 
        for page in sitemap.Pages:
            page_id_str = str(page.id)
            page_section_map[page_id_str] = []
            if page.sections:
                valid_pages_for_gen.append(page)
                for section in page.sections:
                    section_id_str = str(section.id)
                    page_section_map[page_id_str].append(section_id_str)
                    tasks.append(generate_section_html(section, page, project_context))
            else:
                 logging.warning(f"Page '{page.pageName}' (ID: {page.id}) has no sections. Skipping generation for this page.")

        if not tasks:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="No sections found in any page of the provided sitemap data.")

        # --- Execute Generation Tasks Concurrently ---
        logging.info(f"Generating HTML for {len(tasks)} sections across {len(valid_pages_for_gen)} pages concurrently...")
        results: List[Tuple[str, str, str]] = await asyncio.gather(*tasks, return_exceptions=False)

        # --- Process Results ---
        section_html_map: Dict[Tuple[str, str], str] = {} # (page_id, section_id) -> html_string
        successful_generations = 0
        for page_id, section_id, html_content in results:
            section_html_map[(page_id, section_id)] = html_content
            if "Error generating content for" not in html_content:
                successful_generations += 1
        logging.info(f"Finished gathering results. Successfully generated content for {successful_generations}/{len(tasks)} sections.")

        final_page_html_map: Dict[str, str] = {}

        for page in valid_pages_for_gen:
            page_id_str = str(page.id)
            page_html_parts = []

            # HTML Boilerplate
            page_html_parts.append("<!DOCTYPE html>")
            page_html_parts.append("<html lang='en'>")
            page_html_parts.append("<head>")
            page_html_parts.append("  <meta charset='UTF-8'>")
            # page_html_parts.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
            page_html_parts.append('  <script src="https://cdn.tailwindcss.com"></script>')
            page_html_parts.append(f"  <title>{project_context.get('business_name', '')}</title>")
            page_html_parts.append("</head>")
            page_html_parts.append("<body class='bg-gray-100 font-sans'>")

            # page_html_parts.append(f"\n<!-- Start Page Content: {page.pageName} (ID: {page_id_str}) -->")
            # page_html_parts.append(f"<main id='page-content-{page_id_str}' class='container mx-auto p-4 md:p-8'>")
            # page_html_parts.append(f"  <h1 class='text-3xl md:text-4xl font-bold mb-6 md:mb-8 text-gray-800'>{page.pageName}</h1>")

            if page_id_str in page_section_map:
                for section_id_str in page_section_map[page_id_str]:
                    html_content = section_html_map.get((page_id_str, section_id_str))
                    if html_content:
                        page_html_parts.append(f"\n    <!-- Section ID: {section_id_str} -->")
                        page_html_parts.append(f"    {html_content}")
                    else:
                        logging.error(f"Critical: Missing HTML map entry for generated section {section_id_str} on page {page_id_str}")
                        original_section_title = next((s.title for s in page.sections if str(s.id) == section_id_str), 'Unknown Section')
                        page_html_parts.append(f"    <section id='section-{page_id_str}-{section_id_str}' class='bg-red-200 p-4 border border-red-400 text-red-800'>Internal error assembling content for section '{original_section_title}'.</section>")

            page_html_parts.append("</main>")
            page_html_parts.append(f"<!-- End Page Content: {page.pageName} -->\n")

            page_html_parts.append("</body>")
            page_html_parts.append("</html>")

            final_page_html_map[page_id_str] = "\n".join(page_html_parts)
            logging.info(f"Assembled HTML for page '{page.pageName}' (ID: {page_id_str})")

        if not final_page_html_map:
             logging.error(f"Failed to assemble HTML for any page in project {actual_project_id}, although sections were present.")
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                 detail="Failed to generate or assemble HTML content for the pages.")

        logging.info(f"Successfully generated and assembled {len(final_page_html_map)} pages for project {actual_project_id}")

        return MultiPageWebsiteResponse(page_html_map=final_page_html_map, project_id=actual_project_id)

    except HTTPException as http_exc:
        logging.error(f"HTTPException during website creation for sitemap {sitemap_id_from_request}: {http_exc.detail}", exc_info=False) # No need for stack trace for HTTP exceptions usually
        raise http_exc
    except ValueError as ve:
        logging.error(f"ValueError during website creation for sitemap {sitemap_id_from_request}: {str(ve)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid data format: {str(ve)}")
    except Exception as e:
        logging.error(f"Unexpected error creating website for sitemap {sitemap_id_from_request} by user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error during website creation.")