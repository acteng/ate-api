from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://ate:password@localhost/ate"
    create_database_schema: bool = False
    oidc_server_metadata_url: str = (
        "https://dev.identity.api.activetravelengland.gov.uk/.well-known/openid-configuration"
    )
    resource_server_identifier: str = "https://dev.api.activetravelengland.gov.uk"
    docs_username: str | None = None
    docs_password: str | None = None

    model_config = SettingsConfigDict(frozen=True, env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
