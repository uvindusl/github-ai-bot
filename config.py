from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    github_app_id: str
    github_webhook_secret: str
    github_private_key_path: str
    gemini_api_key: str

    class Config:
        env_file = '.env'


settings = Settings()