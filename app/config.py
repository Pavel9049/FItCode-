from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional


class Settings(BaseSettings):
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    run_mode: str = Field("polling", alias="RUN_MODE")  # polling | webhook
    webhook_base_url: Optional[str] = Field(None, alias="WEBHOOK_BASE_URL")
    port: int = Field(8080, alias="PORT")

    database_url: Optional[str] = Field(None, alias="DATABASE_URL")
    redis_url: Optional[str] = Field(None, alias="REDIS_URL")

    admin_ids: List[int] = Field(default_factory=list, alias="ADMIN_IDS")

    stripe_api_key: Optional[str] = Field(None, alias="STRIPE_API_KEY")
    stripe_webhook_secret: Optional[str] = Field(None, alias="STRIPE_WEBHOOK_SECRET")

    yookassa_shop_id: Optional[str] = Field(None, alias="YOOKASSA_SHOP_ID")
    yookassa_secret_key: Optional[str] = Field(None, alias="YOOKASSA_SECRET_KEY")

    google_application_credentials: Optional[str] = Field(None, alias="GOOGLE_APPLICATION_CREDENTIALS")

    support_chat_id: Optional[int] = Field(None, alias="SUPPORT_CHAT_ID")

    scheduler_enabled: bool = Field(True, alias="SCHEDULER_ENABLED")
    broadcast_interval_hours: int = Field(4, alias="BROADCAST_INTERVAL_HOURS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()