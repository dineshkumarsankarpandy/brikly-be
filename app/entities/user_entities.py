from sqlalchemy import Column, Integer, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.core.db_setup import Base
import bcrypt

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mail = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


    # Relationship: One user can have many sitemaps
    sitemaps = relationship("Sitemap", back_populates="creator", cascade="all, delete")

    @staticmethod
    def hash_password(password: str)->str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    @staticmethod
    def verify_password(password: str, hashed_password: str):
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    
    
