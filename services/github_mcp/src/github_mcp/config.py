from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    github_token: str
    github_username: str
    host: str = "0.0.0.0"
    port: int = 8006
    
    class Config:
        env_file = ".env"

settings = Settings()