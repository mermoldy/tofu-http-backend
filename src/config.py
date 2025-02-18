import functools
import pathlib
import typing

import lazy_object_proxy
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import PydanticBaseSettingsSource
from pydantic_settings import SettingsConfigDict
from pydantic_settings import TomlConfigSettingsSource

DEFAULT_MINIO_BUCKET = "e1cc89bb-b9f5-4b29-8163-c3e8da21bbba"
"""A bucked in a public MinIO storage."""


class Config(BaseSettings):
    """The application configuration."""

    model_config = SettingsConfigDict(
        toml_file=pathlib.Path("/Users/mermoldy/Projects/tofu-http-backend/config.toml")
    )

    # Main app config.
    log_level: str = Field(default="info")

    # Minio connection config.
    minio_host: str = Field(default="play.min.io")
    minio_bucket: str = Field(default=DEFAULT_MINIO_BUCKET)
    minio_access_key: str = Field()
    minio_secret_key: str = Field()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: typing.Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


@functools.lru_cache
def get_config() -> Config:
    """Read the configuration."""
    return Config(**{})


config: "Config" = lazy_object_proxy.Proxy(get_config)
"""Global config instance."""
