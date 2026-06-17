from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Ethara API"
    debug: bool = False

    database_url: str = "postgresql://postgres:postgres@localhost:5432/ethara"
    low_stock_threshold: int = 10


settings = Settings()
