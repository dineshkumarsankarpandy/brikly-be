from app.core.db_setup import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP,JSON,func,ForeignKey
from sqlalchemy.orm import relationship



class Sitemap(Base):
    __tablename__ = 'sitemap'

    id = Column(Integer,primary_key=True,nullable=False)
    project_name = Column(String,nullable=False)
    project_description = Column(String,nullable=False)
    no_of_pages = Column(Integer,default=0)
    sitemap_data = Column(JSON,nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer)
    deleted_at = Column(TIMESTAMP)
    deleted_by = Column(Integer)

    creator = relationship("User", back_populates="sitemaps")


