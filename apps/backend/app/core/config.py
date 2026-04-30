from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str

    livekit_url: str
    livekit_public_url: str = ""
    livekit_api_key: str
    livekit_api_secret: str

    openai_api_key: str

    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
