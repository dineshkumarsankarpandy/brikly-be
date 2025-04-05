from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class SectionData(BaseModel):
    id: str|int
    sectionName: str = Field(..., alias='title')
    section_description: str = Field(..., alias='description')

class PageData(BaseModel):
    id: str
    pageName: str = Field(..., alias='label')
    sections: List[SectionData]

class SitemapStructure(BaseModel):
    Pages: List[PageData]

class CreateWebsiteRequest(BaseModel):
    project_id : int
    sitemap : SitemapStructure
    project_description: Optional[str]= None
    business_name : Optional[str] = None

class WebsiteResponse(BaseModel):
    code: str
    project_id: int

class MultiPageWebsiteResponse(BaseModel):
     page_html_map: Dict[str, str]
     project_id: int

class SectionHtmlResponse(BaseModel):
    html_code: str




