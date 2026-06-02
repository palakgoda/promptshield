import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # The port PromptShield will run on locally
    PORT: int = 8080
    
    # Target AI Provider configurations
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Fallback default target if needed
    DEFAULT_PROVIDER_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai"

    # Tell Pydantic to look for a .env file right in the root directory!
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()