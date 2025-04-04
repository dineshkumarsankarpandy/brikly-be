from sqlalchemy import Column, Integer, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.core.db_setup import Base
import bcrypt

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mail = Column(Text, unique=True, nullable=False, index=True)
    password = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship: One user can create many projects
    # Consider delete-orphan if projects should be deleted when removed from user's list in session
    projects = relationship("Project", back_populates="creator", cascade="all, delete")

    # Relationship: One user can create many sitemaps (less direct now, linked via Project)
    # You might remove this if you primarily manage sitemaps via projects
    # sitemaps = relationship("Sitemap", back_populates="creator", cascade="all, delete") # Commented out as maybe redundant

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.mail}')>"