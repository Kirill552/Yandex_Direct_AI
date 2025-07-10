"""
Конфигурация приложения
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv("config.env")


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # OpenAI API
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Yandex Direct API
    yandex_direct_token: str = os.getenv("YANDEX_DIRECT_TOKEN", "")
    yandex_direct_sandbox_token: str = os.getenv("YANDEX_DIRECT_SANDBOX_TOKEN", "")
    yandex_direct_sandbox_mode: bool = os.getenv("YANDEX_DIRECT_SANDBOX_MODE", "true").lower() == "true"
    yandex_direct_api_url_sandbox: str = os.getenv("YANDEX_DIRECT_API_URL_SANDBOX", "https://api-sandbox.direct.yandex.com/json/v5/")
    yandex_direct_api_url_production: str = os.getenv("YANDEX_DIRECT_API_URL_PRODUCTION", "https://api.direct.yandex.com/json/v5/")
    
    # Настройки логирования
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # FastAPI Settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8001"))
    
    # Telegram
    telegram_bot_token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    owner_telegram_id: Optional[int] = int(os.getenv("OWNER_TELEGRAM_ID", "0")) if os.getenv("OWNER_TELEGRAM_ID") else None
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./campaigns.db")
    
    # Настройки проекта
    project_name: str = os.getenv("PROJECT_NAME", "Yandex Direct AI Campaign Manager")
    version: str = os.getenv("VERSION", "1.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = "config.env"


# Глобальный экземпляр настроек
settings = Settings() 