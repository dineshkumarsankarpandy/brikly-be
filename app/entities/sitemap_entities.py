from app.core.db_setup import Base
from sqlalchemy import Column, Integer, String,Boolean,Index, TIMESTAMP, JSON, func, ForeignKey, Text
from sqlalchemy.orm import relationship

class Sitemap(Base):
    __tablename__ = 'sitemap'

    __table_args__ = (Index('ix_sitemap_project_id_is_active', "project_id", "is_active"),)
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    project_description = Column(Text, nullable=True) 
    no_of_pages = Column(Integer, default=0)
    sitemap_data = Column(JSON, nullable=True)     
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True) 
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)
    deleted_by = Column(Integer, nullable=True) 

    project = relationship("Project", back_populates="sitemaps")



    # creator = relationship("User", back_populates="sitemaps") # You might not need both user links

    def __repr__(self):
        return f"<Sitemap(id={self.id}, project_id={self.project_id})>"