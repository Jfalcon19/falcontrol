from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FALCONTROL_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    # App
    env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    version: str = "0.1.0"

    # Security
    secret_key: str = "insecure-dev-key-change-in-production"
    jwt_secret: str = "insecure-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Database — no FALCONTROL_ prefix; Docker Compose and the OS use bare POSTGRES_* names
    postgres_host: str = Field("db", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, validation_alias="POSTGRES_PORT")
    postgres_db: str = Field("falcontrol", validation_alias="POSTGRES_DB")
    postgres_user: str = Field("falcontrol", validation_alias="POSTGRES_USER")
    postgres_password: str = Field("changeme", validation_alias="POSTGRES_PASSWORD")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis / Celery — no FALCONTROL_ prefix
    redis_host: str = Field("redis", validation_alias="REDIS_HOST")
    redis_port: int = Field(6379, validation_alias="REDIS_PORT")
    redis_db: int = Field(0, validation_alias="REDIS_DB")

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def celery_broker_url(self) -> str:
        return self.redis_url

    @property
    def celery_result_backend(self) -> str:
        return self.redis_url

    # CORS
    cors_origins: list[str] = ["http://localhost", "http://localhost:5173"]

    # First admin (created on startup if no users exist)
    first_admin_email: str = "admin@example.com"
    first_admin_password: str = "changeme"


settings = Settings()
