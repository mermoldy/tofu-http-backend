import datetime

from src.app.state.types import LockInfo


def test_lock_info_load() -> None:
    data = {
        "id": "abcd1234",
        "operation": "Apply",
        "info": "Some info",
        "who": "test@machine",
        "version": "2.0.0",
        "created": "2025-02-19T15:47:52.732586Z",
        "path": "/some/path",
    }

    lock = LockInfo(**data)  # type: ignore
    serialized = lock.model_dump(by_alias=True)

    assert serialized.get("ID") == "abcd1234"
    assert serialized.get("Operation") == "Apply"
    assert serialized.get("Created") == datetime.datetime(
        2025, 2, 19, 15, 47, 52, 732586, tzinfo=datetime.UTC
    )
