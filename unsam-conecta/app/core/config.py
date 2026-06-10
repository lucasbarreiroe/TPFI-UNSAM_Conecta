from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "UNSAM Conecta API"
    ENVIRONMENT: str = "development"
    
    # JWT Settings
    SECRET_KEY: str = "your_secure_random_string" # En producción esto viene del .env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Email Settings (NUEVO)
    SMTP_EMAIL: str = ""
    SMTP_PASSWORD: str = ""
    
    # Database Settings
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()