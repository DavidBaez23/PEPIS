import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = ""
    # Model configuration
    LLM_MODEL: str = "google/gemini-2.5-flash"
    # LLM_MODEL: str = "liquid/lfm-40b"
    MAX_TOKENS: int = 1500
    
    class Config:
        env_file = ".env"

settings = Settings()
