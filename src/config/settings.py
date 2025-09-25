from pydantic_settings import BaseSettings
import os

PLAID_ENV = "production"

env_files = {
    "sandbox": ".env.sandbox",
    "development": ".env.development",
    "production": ".env.production"
}

env_file = env_files.get(PLAID_ENV, ".env.sandbox")
if not os.path.exists(env_file):
    raise FileNotFoundError(f"Env file {env_file} not found")

class Settings(BaseSettings):
    
    APP_PASSWORD: str = ""
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    PLAID_ENV: str = PLAID_ENV
    PLAID_ACCESS_TOKEN: str = ""
    PLAID_ITEM_ID: str = ""
    DATABASE_URL: str = ""

    class Config:
        env_file = env_file
        env_file_encoding = "utf-8"

settings = Settings()