from pydantic_settings import BaseSettings
import os

PLAID_ENV = "production"

env_files = {
    "sandbox": ".env.sandbox",
    "development": ".env.development",
    "production": ".env.production"
}

schema_mapping = {
    "sandbox": "canada_budget_tracker_sandbox",
    "development": "canada_budget_tracker_development",
    "production": "canada_budget_tracker_production"
}

env_file = env_files.get(PLAID_ENV, ".env.sandbox")
if not os.path.exists(env_file):
    raise FileNotFoundError(f"Env file {env_file} not found")

class Settings(BaseSettings):

    ADMIN_PASSWORD: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    PLAID_ENV: str = PLAID_ENV
    PLAID_ACCESS_TOKEN: str = ""
    PLAID_ITEM_ID: str = ""
    DATABASE_URL: str = ""

    class Config:
        env_file = env_file
        env_file_encoding = "utf-8"

    @property
    def DATABASE_SCHEMA(self) -> str:
        return schema_mapping.get(self.PLAID_ENV, "canada_budget_tracker_sandbox")

settings = Settings()