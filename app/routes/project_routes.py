from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.project_models import CreateProjectRequest, EditProjectRequest
from app.entities.project_entities import Project
from app.entities.user_entities import User
from app.core.db_setup import get_db
from app.core.config import logging
from app.services.auth_service import get_current_user


router = APIRouter(prefix="/projects", 
                   tags=["Projects"],
                   dependencies=[Depends(get_current_user)]
                   )




@router.post("/create-project", status_code=status.HTTP_201_CREATED)
async def create_project(
    data: CreateProjectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    try:
        logging.info(f"User {current_user.id} creating project: {data.project_name}")
        new_project = Project(
            project_name=data.project_name,
            created_by=current_user.id 
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        logging.info(f"Project created successfully with ID: {new_project.id}")
        return {
            "id": new_project.id,
            "project_name": new_project.project_name,
            "created_at":new_project.created_at,
            "updated_at":new_project.updated_at,
            "created_by":new_project.created_by,
            "message":"Project created successfully"
        }
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating project for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error creating project")
    




@router.put("/edit-project/{project_id}",)
async def edit_project_name(
    project_id: int,
    data: EditProjectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logging.info(f"User {current_user.id} attempting to edit project ID: {project_id}")
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            logging.warning(f"Edit failed: Project ID {project_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        if project.created_by != current_user.id:
            logging.warning(f"Authorization failed: User {current_user.id} tried to edit project {project_id} owned by {project.created_by}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this project")

        project.project_name = data.project_name
        project.updated_by = current_user.id 
        db.commit()
        db.refresh(project)
        logging.info(f"Project ID {project_id} name updated to '{data.project_name}' by user {current_user.id}")
        return {
             "id": project.id,
            "project_name": project.project_name,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "created_by": project.created_by,
            "message": "Project name updated successfully"
        }
    except HTTPException as http_exc:
        raise http_exc 
    except Exception as e:
        db.rollback()
        logging.error(f"Error editing project {project_id} for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error editing project")




@router.get("/{project_id}")
async def get_project_details(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logging.info(f"User {current_user.id} requesting details for project ID: {project_id}")
        project = db.query(Project)\
                    .options(joinedload(Project.sitemap))\
                    .filter(Project.id == project_id)\
                    .first()

        if not project:
            logging.warning(f"Get details failed: Project ID {project_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        if project.created_by != current_user.id:
            logging.warning(f"Authorization failed: User {current_user.id} tried to access project {project_id} owned by {project.created_by}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

        logging.info(f"Successfully retrieved details for project ID: {project_id}")
        return project 

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"Error getting project details {project_id} for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error retrieving project details")



@router.get("/")
async def get_user_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all projects created by the logged-in user."""
    try:
        logging.info(f"User {current_user.id} requesting their projects list.")
        projects = db.query(Project)\
                     .filter(Project.created_by == current_user.id)\
                     .order_by(Project.created_at.desc())\
                     .all()

        logging.info(f"Found {len(projects)} projects for user {current_user.id}.")
        return {"data":projects, "message":f"Found {len(projects)} projects."}

    except Exception as e:
        logging.error(f"Error listing projects for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error listing projects")



@router.delete("/delete-project/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logging.info(f"User {current_user.id} attempting to delete project ID: {project_id}")
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            logging.warning(f"Delete failed: Project ID {project_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        # Authorization check
        if project.created_by != current_user.id:
            logging.warning(f"Authorization failed: User {current_user.id} tried to delete project {project_id} owned by {project.created_by}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this project")

        db.delete(project) 
        logging.info(f"Project ID {project_id} deleted successfully by user {current_user.id}.")
        return None

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        db.rollback()
        logging.error(f"Error deleting project {project_id} for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error deleting project")