from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    VK_TOKEN: str
    VK_CHAT_ID: int

    TG_BOT_TOKEN: str
    TG_CHAT: int

    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()   # pyright: ignore[reportCallIssue]