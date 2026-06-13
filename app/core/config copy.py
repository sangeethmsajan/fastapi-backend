from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Offensive Automation Framework", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    debug: bool = Field(default=True, alias="DEBUG")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    frontend_origin: str = Field(default="http://localhost:3000", alias="FRONTEND_ORIGIN")

    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=3306, alias="DB_PORT")
    db_name: str = Field(alias="DB_NAME")

    celery_broker_url: str = Field(default="redis://127.0.0.1:6379/0", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://127.0.0.1:6379/0", alias="CELERY_RESULT_BACKEND")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()