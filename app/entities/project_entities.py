from app.core.db_setup import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    project_name = Column(String, nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    # Ensure created_by references the users table correctly
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True) # Or CASCADE if preferred
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    # updated_by could also be a ForeignKey to users if needed
    updated_by = Column(Integer, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)
    deleted_by = Column(Integer, nullable=True) # Could be FK to users

    # Relationship back to the User who created it
    creator = relationship("User", back_populates="projects")

    # Relationship to the Sitemap (one-to-one)
    # cascade="all, delete-orphan": If project is deleted, delete sitemap. If sitemap removed from project in session, delete sitemap.
    sitemap = relationship("Sitemap", back_populates="project", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.project_name}')>"