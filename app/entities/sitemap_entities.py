from app.core.db_setup import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON, func, ForeignKey, Text
from sqlalchemy.orm import relationship

class Sitemap(Base):
    __tablename__ = 'sitemap'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False)

    project_description = Column(Text, nullable=True) # Keep brief/description if needed specifically for sitemap context
    no_of_pages = Column(Integer, default=0)
    sitemap_data = Column(JSON, nullable=True) # Can be nullable initially
    created_at = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True) # Or CASCADE
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, nullable=True) # Could be FK to users
    deleted_at = Column(TIMESTAMP, nullable=True)
    deleted_by = Column(Integer, nullable=True) # Could be FK to users

    project = relationship("Project", back_populates="sitemap")

    # creator = relationship("User", back_populates="sitemaps") # You might not need both user links

    def __repr__(self):
        return f"<Sitemap(id={self.id}, project_id={self.project_id})>"