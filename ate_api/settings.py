from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    oidc_server_metadata_url: str = "https://ate-api-dev.uk.auth0.com/.well-known/openid-configuration"

    model_config = SettingsConfigDict(frozen=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
