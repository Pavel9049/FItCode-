from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    run_mode: str = Field("polling", alias="RUN_MODE")  # polling | webhook
    webhook_base_url: Optional[str] = Field(None, alias="WEBHOOK_BASE_URL")
    port: int = Field(8080, alias="PORT")

    database_url: Optional[str] = Field(None, alias="DATABASE_URL")
    redis_url: Optional[str] = Field(None, alias="REDIS_URL")

    admin_ids: str = Field(default="", alias="ADMIN_IDS")

    stripe_api_key: Optional[str] = Field(None, alias="STRIPE_API_KEY")
    stripe_webhook_secret: Optional[str] = Field(None, alias="STRIPE_WEBHOOK_SECRET")

    yookassa_shop_id: Optional[str] = Field(None, alias="YOOKASSA_SHOP_ID")
    yookassa_secret_key: Optional[str] = Field(None, alias="YOOKASSA_SECRET_KEY")

    tinkoff_terminal_key: Optional[str] = Field(None, alias="TINKOFF_TERMINAL_KEY")
    tinkoff_secret_key: Optional[str] = Field(None, alias="TINKOFF_SECRET_KEY")

    nowpayments_api_key: Optional[str] = Field(None, alias="NOWPAYMENTS_API_KEY")

    google_application_credentials: Optional[str] = Field(None, alias="GOOGLE_APPLICATION_CREDENTIALS")

    support_chat_id: Optional[int] = Field(None, alias="SUPPORT_CHAT_ID")

    scheduler_enabled: bool = Field(True, alias="SCHEDULER_ENABLED")
    broadcast_interval_hours: int = Field(4, alias="BROADCAST_INTERVAL_HOURS")

    @property
    def admin_ids_list(self) -> List[int]:
        """Получить список ID администраторов"""
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(',') if x.strip().isdigit()]


settings = Settings()