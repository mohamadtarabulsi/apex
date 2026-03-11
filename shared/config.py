"""Centralized configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "apex"
    postgres_user: str = "apex"
    postgres_password: str = "apex_dev_password"

    # QuestDB
    questdb_host: str = "questdb"
    questdb_ilp_port: int = 9009
    questdb_rest_port: int = 9000
    questdb_pg_port: int = 8812

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379

    # NATS
    nats_url: str = "nats://nats:4222"

    # Broker APIs
    alpaca_api_key: str = ""
    alpaca_api_secret: str = ""
    alpaca_base_url: str = "https://paper-api.alpaca.markets"

    # Prediction Markets
    kalshi_api_key: str = ""
    kalshi_private_key_path: str = ""
    polymarket_private_key: str = ""

    # AI Models
    anthropic_api_key: str = ""
    perplexity_api_key: str = ""
    openai_api_key: str = ""
    google_ai_api_key: str = ""
    xai_api_key: str = ""
    deepseek_api_key: str = ""

    # Data APIs
    fred_api_key: str = ""
    news_api_key: str = ""
    gnews_api_key: str = ""
    tradier_api_token: str = ""

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # System
    log_level: str = "INFO"
    environment: str = "development"

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
