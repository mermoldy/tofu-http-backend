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
"""Default bucked in a MinIO storage."""


class Config(BaseSettings):
    """The application configuration."""

    model_config = SettingsConfigDict(
        toml_file=pathlib.Path("/Users/mermoldy/Projects/tofu-http-backend/config.toml")
    )

    # Main app config.
    log_level: str = Field(default="info", description="The log level.")
    storage_backend: typing.Literal["minio"] = Field(
        default="minio", description="The remote storage backend used for storing state files."
    )
    lock_backend: typing.Literal["minio"] = Field(
        default="minio", description="The remote storage backend used for state file locking."
    )

    # Minio connection config.
    minio_host: str = Field(default="play.min.io", description="The MinIO host.")
    minio_bucket: str = Field(
        default=DEFAULT_MINIO_BUCKET, description="Bucked in a MinIO storage."
    )
    minio_access_key: str = Field(description="The MinIO access key.")
    minio_secret_key: str = Field(description="The MinIO private secret key.")

    @classmethod
    def settings_customise_sources(
        cls, settings_cls: type[BaseSettings], *args, **kwargs
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


@functools.lru_cache
def get_config() -> Config:
    """Read the configuration."""
    return Config(**{})


config: "Config" = lazy_object_proxy.Proxy(get_config)
"""Global config instance."""
