import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "Bank-to-TallyPrime Automation"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./bank_tally.db"
    
    # TallyPrime Settings
    TALLY_HOST: str = "localhost"
    TALLY_PORT: int = 9000
    TALLY_COMPANY: str = "Pawan Glasses"
    TALLY_SIMULATION_MODE: bool = False
    DEFAULT_BANK_LEDGER: str = "HDFC Bank Account"
    
    # Approval & Automation thresholds
    AUTO_APPROVE_THRESHOLD: float = 0.95
    
    # Storage & Logging
    UPLOAD_DIR: str = "./uploads"
    SECRET_KEY: str = "bank-tally-secret-key-change-in-production"
    LOG_LEVEL: str = "INFO"


settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("./logs", exist_ok=True)
