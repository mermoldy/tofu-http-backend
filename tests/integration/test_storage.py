"""The integration tests for the storage backends."""

from src import storage

import uuid
import pytest


def gen_key() -> str:
    return f"pytest-{uuid.uuid4()}"


class TestMinioStorageBackend:
    def test_create(self) -> None:
        """Test creating a minio object."""
        key = gen_key()
        backend = storage.MinioStorageBackend()

        backend.create(key, b"123")
        assert backend.get(key) == b"123"

    def test_get(self) -> None:
        """Test reading minio object."""
        key = gen_key()
        backend = storage.MinioStorageBackend()

        with pytest.raises(storage.NotFound):
            backend.get(key)

        backend.create(key, b"123")
        assert backend.get(key) == b"123"

    def test_delete(self) -> None:
        """Test deleting a minio object."""
        key = gen_key()
        backend = storage.MinioStorageBackend()

        backend.create(key, b"123")
        backend.delete(key)

        with pytest.raises(storage.NotFound):
            backend.get(key)
