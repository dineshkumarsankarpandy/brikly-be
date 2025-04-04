# model.py
from pydantic import BaseModel, Field
from typing import Optional, List,Dict,Any
from enum import Enum


class FontStyle(BaseModel):
    description: str


class CSSProperties(BaseModel):
    font_family: str
    font_size: str
    font_weight: Optional[str] = None


class CSSExample(BaseModel):
    selector: str
    properties: CSSProperties


class FontExample(BaseModel):
    css: CSSExample


class BrandLogoFont(BaseModel):
    name: str
    logo_name: str
    style: FontStyle
    best_for: str
    link: str
    example: FontExample


class FontWeight(int, Enum):
    Thin = 100
    ExtraLight = 200
    Light = 300
    Regular = 400
    Medium = 500
    SemiBold = 600
    Bold = 700
    ExtraBold = 800
    Black = 900


class ScaleEnum(str, Enum):
    MINOR_SECOND = "1.067"
    MAJOR_SECOND = "1.125"
    MINOR_THIRD = "1.200"
    MAJOR_THIRD = "1.250"
    PERFECT_FOURTH = "1.333"
    AUGMENTED_FOURTH = "1.414"
    PERFECT_FIFTH = "1.500"
    GOLDEN_RATIO = "1.618"
    CUSTOM = "custom"


class Font(BaseModel):
    font_family: str
    base_fontsize: int
    font_weight: List[FontWeight]
    line_height: int
    typescale_ratio: ScaleEnum


class BrandColor(BaseModel):
    primary_color: str
    secondary_color: str


class ColorPalette(int, Enum):
    Monochromatic = 1
    Analogous = 2
    Complementary = 3
    Triadic = 4
    Tetradic = 5


class BrandColorSchema(BaseModel):
    colors: BrandColor
    ColorPalette: ColorPalette
    ColorPalette_description: str


class VisualBrandGuidelines(BaseModel):
    Logo_typeface: List[BrandLogoFont]
    font: Font
    colors: BrandColorSchema


class ProjectBrief(BaseModel):
    business_name: str
    business_description: str
    website_goal: str
    target_audience: str
    VisualBrandGuidelines: VisualBrandGuidelines
    pageCount: Optional[int] = None
    language: Optional[str] = None


class SectionName(str, Enum):
    Navbar = "Navbar"
    Hero_Header_Section = "Hero Header Section"
    # ... (Include all other SectionName enum values from your original code)
    Footer = "Footer"
    Comparison_Section = "Comparison Section"


class SectionOutline(BaseModel):
    section_name: SectionName = Field(
        description="Use only the section names to name the section"
    )
    section_instruction: str = Field(
        description="Instruction to describe what the section should contain"
    )
    section_description: str = Field(
        description="Description about the section and its children"
    )


class Page(BaseModel):
    page_id: int
    Pagename: str
    sections: List[SectionOutline]


class Pages(BaseModel):
    websitename: str
    Numberofpages: int
    pages: List[Page]


class SitemapGenerator(BaseModel):
    business_name: str = Field(..., alias="businessName")
    business_description: str = Field(..., alias="businessDescription")
    sitemap_prompt: Optional[str] = Field(None, alias="prompt")
    page: Optional[int] = None
    language: Optional[str] = None


class saveSitemap(BaseModel):
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    no_of_pages: Optional[int] = None
    sitemap_data: Optional[Dict[str, Any]] = None
