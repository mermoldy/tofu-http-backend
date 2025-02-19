"""The integration tests for the lock backends."""

from src import lock

import uuid
import pytest


def gen_key() -> str:
    return f"pytest-{uuid.uuid4()}"


class TestMinioLockBackend:
    def test_lock(self) -> None:
        """Test creating a minio lock ."""
        key = gen_key()
        backend = lock.MinioLockBackend()
        backend.lock(key, {"id": "myid1", "who": "pytest"})

        with pytest.raises(lock.AlreadyLocked) as err:
            backend.lock(key, {"id": "myid1", "who": "pytest"})
        assert f"The {key} has lock with ID myid1 by pytest" in str(err)

    def test_unlock(self) -> None:
        """Test removing a minio lock ."""
        key = gen_key()
        backend = lock.MinioLockBackend()

        with pytest.raises(lock.NotLocked) as err:
            backend.unlock(key)
        assert f"The {key} lock not acquired" in str(err)

        backend.lock(key, {"id": "myid1", "who": "pytest"})
        assert backend.unlock(key) == {"id": "myid1", "who": "pytest"}
