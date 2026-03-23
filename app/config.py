from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    database_url: str
    secret_key: str
    refresh_token_secret_key: str
    fernet_key: str
    cors_origins: str = "*"


settings = Settings()
