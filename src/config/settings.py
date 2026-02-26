import os
from dotenv import load_dotenv

# Force load the .env file from the project root
load_dotenv()

class Settings:
    """Central configuration and secrets manager for KaliVibe."""
    
    # Secrets
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    
    # Configurations
    LLM_MODEL: str | None = os.getenv("LLM_MODEL") 

config = Settings()

# Fail fast if critical secrets or configs are missing
if not config.OPENAI_API_KEY:
    raise ValueError("CRITICAL ERROR: OPENAI_API_KEY is not set in the .env file.")

if not config.LLM_MODEL:
    raise ValueError("CRITICAL ERROR: LLM_MODEL is not set in the .env file. Please specify a model (e.g., LLM_MODEL=gpt-4o).")