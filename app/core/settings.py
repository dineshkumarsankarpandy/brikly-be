import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # General App Settings
    APP_NAME: str = os.getenv("APP_NAME", "Sitemap Generator API")
    ENV: str = os.getenv("ENV", "development")

    # Database Settings
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME")

    SECRET_KEY: str= os.getenv("SECRET_KEY")  # Make sure to add SECRET_KEY and ALGORITHM here
    ALGORITHM: str = os.getenv("ALGORITHM")  # Default value for the algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES: str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

    
    @property
    def DATABASE_URL(self):
        from urllib.parse import quote_plus
        password = quote_plus(self.DB_PASSWORD)
        return f'postgresql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    # LLM API Key
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    class Config:
        env_file = ".env"  
settings = Settings()
