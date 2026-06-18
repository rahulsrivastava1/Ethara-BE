from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Ethara API"
    debug: bool = False

    database_url: str = "postgresql://postgres:postgres@localhost:5432/ethara"
    low_stock_threshold: int = 10
    frontend_url: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.frontend_url.split(",")
            if origin.strip()
        ]


settings = Settings()
