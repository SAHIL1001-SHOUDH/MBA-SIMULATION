import os

from pydantic_settings import BaseSettings


class BaseSettingsWrapper(BaseSettings):
    class Config:
        env_file = (
            "MBA_SIMULATION/.env" if os.path.exists("MBA_SIMULATION/.env") else ".env"
        )
        case_sensitive = True
        extra = "allow"
