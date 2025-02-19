"""
The remote storage backend for the HTTP state server.
"""

import functools
import io
from typing import Protocol

import lazy_object_proxy
import minio
import minio.error

from src import errors
from src import log
from src.config import config

__all__ = ["default", "MinioStorageBackend", "Error", "NotFound"]

LOG = log.get_logger(__name__)


class Error(errors.Error):
    """The storage backend error."""


class NotFound(Error):
    """Raised when requested object ID not found."""


class StorageBackend(Protocol):
    """Protocol for storage backends."""

    name: str

    def get(self, key: str) -> bytes:
        """Fetch data for the given `key`."""
        ...

    def create(self, key: str, data: bytes) -> None:
        """Save `data` to the given `key`."""
        ...

    def delete(self, key: str) -> None:
        """Delete data by `key`."""
        ...


class MinioStorageBackend:
    """
    Storage Backend implementation using MinIO.

    Look at how cool this is: https://github.com/minio/minio!
    """

    name = "MinIO"

    def __init__(self) -> None:
        self._client = minio.Minio(
            config.minio_host,
            access_key=config.minio_access_key,
            secret_key=config.minio_secret_key,
        )
        self._bucket_name = config.minio_bucket
        super().__init__()

    def _exists_bucket(self) -> bool:
        """Check if the bucket exists in the MinIO storage."""
        try:
            return self._client.bucket_exists(self._bucket_name)
        except minio.error.MinioException as err:
            raise Error(str(err))

    def _create_bucket(self) -> None:
        """Create the bucket in the MinIO storage."""
        self._client.make_bucket(self._bucket_name)
        LOG.info("Created MinIO bucket.", bucket_name=self._bucket_name)

    def get(self, key: str) -> bytes:
        """Get an object in a MinIO bucket."""
        if not self._exists_bucket():
            raise NotFound(f"The {key} object not found.")

        try:
            return self._client.get_object(self._bucket_name, key).read()
        except minio.error.S3Error as err:
            raise NotFound(str(err))
        except minio.error.MinioException as err:
            raise Error(str(err))

    def create(self, key: str, data: bytes) -> None:
        """Create an object in the MinIO storage."""
        if not self._exists_bucket():
            self._create_bucket()

        try:
            self._client.put_object(
                self._bucket_name, key, io.BytesIO(data), length=len(data), metadata={"Owner": ""}
            )
        except minio.error.MinioException as err:
            raise Error(str(err))

    def delete(self, key: str) -> None:
        """Delete an object from the MinIO storage."""
        if not self._exists_bucket():
            raise NotFound(f"The {key} object not found.")

        try:
            self._client.remove_object(self._bucket_name, key)
        except minio.error.S3Error as err:
            raise NotFound(str(err))
        except minio.error.MinioException as err:
            raise Error(str(err))


@functools.lru_cache
def create_default_backend() -> StorageBackend:
    """Create the default storage backend."""
    match b := config.storage_backend:
        case "minio":
            return MinioStorageBackend()
        case _:
            raise ValueError(f"Unsupported storage backend: {b}")


default: "StorageBackend" = lazy_object_proxy.Proxy(create_default_backend)
"""Default storage backend instance (lazy object)."""
