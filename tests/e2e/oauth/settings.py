from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    resource_server_identifier: str

    model_config = SettingsConfigDict(frozen=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
