from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Empty by default so the web dashboard can start without a token;
    # app/main.py (the bot process) checks this itself and fails clearly.
    telegram_bot_token: str = ""
    xrocket_api_base_url: str = "https://exchange.api.xrocket.exchange"
    # xRocket uses a hyphen in symbol names, e.g. "TON-USDT", "BTC-USDT".
    symbol: str = "TON-USDT"
    collect_interval_seconds: int = 10
    database_url: str = (
        "postgresql+asyncpg://analytics:analytics@postgres:5432/analytics"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, v: str) -> str:
        # Managed hosts (Render, Railway, Heroku-style) hand out plain
        # postgres:// or postgresql:// URLs. SQLAlchemy's async engine
        # needs the asyncpg driver spelled out.
        if v.startswith("postgres://"):
            v = "postgresql://" + v[len("postgres://") :]
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
