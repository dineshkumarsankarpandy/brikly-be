from sqlalchemy import Column, Integer, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.core.db_setup import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mail = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


    # Relationship: One user can have many sitemaps
    sitemaps = relationship("Sitemap", back_populates="creator", cascade="all, delete")
