from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://stockwatch:stockwatch@localhost:5432/stockwatch"
    line_channel_access_token: str = ""
    line_user_id: str = ""
    fugle_api_key: str = ""
    finnhub_api_key: str = ""
    poll_interval: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
