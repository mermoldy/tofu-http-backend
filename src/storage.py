"""
The remote storage backend for the HTTP state sever.

The default backend uses the MinIO server public playground.
"""

import functools
import io

import lazy_object_proxy
import minio
import minio.error

from src import log
from src.config import config

__all__ = ["get_client"]

LOG = log.get_logger(__name__)


class Error(Exception):
    """The storage backend error."""


class NotFound(Error):
    """When requested object ID not found."""


class StorageBackend:
    """The storage backend interface."""

    name: str

    def get(self, state_id: str) -> bytes:
        raise NotImplementedError()

    def create(self, state_id: str, data: bytes) -> None:
        raise NotImplementedError()

    def delete(self, state_id: str) -> None:
        raise NotImplementedError()


class MinioStorageBackend(StorageBackend):
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
        return self._client.bucket_exists(self._bucket_name)

    def _create_bucket(self) -> None:
        self._client.make_bucket(self._bucket_name)
        LOG.info("Created Minio bucket.", bucket_name=self._bucket_name)

    def get(self, state_id: str) -> bytes:
        """Get an object in a minio bucket."""
        if not self._exists_bucket():
            raise NotFound(f"The {state_id} object not found.")

        try:
            data = self._client.get_object(self._bucket_name, state_id)
        except minio.error.S3Error as err:
            raise NotFound(str(err))

        return data.read()

    def create(self, state_id: str, data: bytes) -> None:
        """Create an object in a minio bucket."""
        if not self._exists_bucket():
            self._create_bucket()
        self._client.put_object(
            self._bucket_name, state_id, io.BytesIO(data), length=len(data), metadata={"Owner": ""}
        )

    def delete(self, state_id: str) -> None:
        """Delete an object from a minio bucket."""
        if not self._exists_bucket():
            raise NotFound(f"The {state_id} object not found.")

        try:
            self._client.remove_object(self._bucket_name, state_id)
        except minio.error.S3Error as err:
            raise NotFound(str(err))


@functools.lru_cache
def get_default_storage() -> StorageBackend:
    """Create the storage backend."""
    return MinioStorageBackend()


default: "StorageBackend" = lazy_object_proxy.Proxy(get_default_storage)
"""Default storage backend instance."""
