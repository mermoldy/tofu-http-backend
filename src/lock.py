"""
The remote locking backend for the HTTP state server.
"""

import functools
import typing
from typing import Protocol
from typing import TypedDict

import lazy_object_proxy
import orjson

from src import errors
from src import log
from src import storage
from src.config import config

__all__ = ["default", "Error", "NotFound", "AlreadyLocked", "NotLocked"]

LOG = log.get_logger(__name__)


class Error(errors.Error):
    """The locking backend error."""


class NotFound(Error):
    """Raised when requested object ID not found."""


class AlreadyLocked(Error):
    """Raised when the requested object ID is already locked."""


class NotLocked(Error):
    """Raised when the requested object ID is not locked."""


class LockInfo(TypedDict):
    """Represents the minimal set of fields for lock metainfo."""

    id: str
    who: str


class LockBackend(Protocol):
    """
    Protocol for lock backends.
    """

    name: str

    def lock(self, key: str, metainfo: LockInfo) -> None:
        """Lock the given `key`.

        :param key: The ID for lock to acqiure.
        :param metainfo: The meta information for lock to acqiure.

        :raises :class:`NotFound`
        :raises :class:`AlreadyLocked`
        """
        ...

    def unlock(self, key: str) -> LockInfo:
        """Unlock the given `key`.

        :raises :class:`NotFound`
        :raises :class:`NotLocked`

        :return: The meta information of removed lock.
        """
        ...


class MinioLockBackend:
    """
    Lock Backend implementation using MinIO.

    Since MinIO does not natively support locking, this lock backend uses a simple
    mechanism by placing a `.lock` file in storage alongside the main blob file.
    However, this approach may not be sufficient for high-concurrency applications,
    as it can lead to collisions or race conditions.

    For production-ready locking, a backend that natively supports locks should be used.
    """

    name = "MinIO"

    def __init__(self) -> None:
        self._storage = storage.MinioStorageBackend()
        super().__init__()

    def lock(self, key: str, metainfo: LockInfo) -> None:
        """Lock the given `key` in a MinIO bucket.

        :param key: The ID for lock to acqiure.
        :param metainfo: The meta information for lock to acqiure.

        :raises :class:`NotFound`
        :raises :class:`AlreadyLocked`
        """
        lock_key = f"{key}.lock"
        try:
            try:
                existing_metainfo = orjson.loads(self._storage.get(lock_key))
                if existing_metainfo:
                    id_ = existing_metainfo.get("id", "null")
                    who = existing_metainfo.get("who", "unknown")
                    raise AlreadyLocked(f"The {key} has lock with ID {id_} by {who}.")
            except storage.NotFound as err:
                pass

            self._storage.create(lock_key, orjson.dumps(metainfo))
        except storage.Error as err:
            raise Error(str(err))

    def unlock(self, key: str) -> LockInfo:
        """Create an object in a minio bucket.

        :raises :class:`NotFound`
        :raises :class:`NotLocked`

        :return: The meta information of removed lock.
        """
        lock_key = f"{key}.lock"
        try:
            metainfo = orjson.loads(self._storage.get(lock_key))
            if not isinstance(metainfo, dict):
                raise ValueError("Unexpected metainfo type.")
            self._storage.delete(lock_key)
            return typing.cast(LockInfo, metainfo)
        except storage.NotFound as err:
            raise NotLocked(f"The {key} lock not acquired.")
        except storage.Error as err:
            raise Error(str(err))
        except ValueError as err:
            raise Error("Cannot decode the lock metainfo. %s", str(err))


@functools.lru_cache
def create_default_backend() -> LockBackend:
    """Create the default lock backend."""
    match b := config.lock_backend:
        case "minio":
            return MinioLockBackend()
        case _:
            raise ValueError(f"Unsupported lock backend: {b}")


default: "LockBackend" = lazy_object_proxy.Proxy(create_default_backend)
"""Default lock backend instance (lazy object)."""
