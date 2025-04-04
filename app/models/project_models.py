from pydantic import BaseModel, Field


class CreateProjectRequest(BaseModel):
    project_name: str = Field(..., min_length=1, example="My New Website")

class EditProjectRequest(BaseModel):
    project_name: str = Field(..., min_length=1, example="My Renamed Website")

