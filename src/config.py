import functools
import pathlib
import typing

import lazy_object_proxy
from pydantic import Field
from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import EnvSettingsSource
from pydantic_settings import PydanticBaseSettingsSource
from pydantic_settings import SettingsConfigDict
from pydantic_settings import TomlConfigSettingsSource

DEFAULT_MINIO_BUCKET = "e1cc89bb-b9f5-4b29-8163-c3e8da21bbba"
"""Default bucked in a MinIO storage."""


class Config(BaseSettings):
    """The application configuration."""

    model_config = SettingsConfigDict(
        toml_file=pathlib.Path("config.toml"), env_prefix="TOFU_HTTP_"
    )

    # Main app config.
    log_level: str = Field(default="info", description="The log level.")
    username: str | None = Field(
        default=None, description="The username for HTTP basic authentication."
    )
    password: str | None = Field(
        default=None, description="The password for HTTP basic authentication"
    )

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

    @model_validator(mode="after")
    def check_auth_credentials(self) -> "Config":
        """Check that both 'username' and 'password' are set together or left empty."""
        if bool(self.username) is not bool(self.password):
            raise ValueError("Both 'username' and 'password' must be set together or left empty.")
        return self

    @classmethod
    def settings_customise_sources(
        cls, settings_cls: type[BaseSettings], *args, **kwargs
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (EnvSettingsSource(settings_cls), TomlConfigSettingsSource(settings_cls))


@functools.lru_cache
def get_config() -> Config:
    """Read the configuration."""
    return Config(**{})


config: "Config" = lazy_object_proxy.Proxy(get_config)
"""Global config instance."""
