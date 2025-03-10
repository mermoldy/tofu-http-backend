"""The HTTP state API routes."""

import typing

import orjson
import pydantic_core
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.responses import Response

from src import lock
from src import log
from src import storage

from . import service
from . import types

LOG = log.get_logger(__name__)

router = APIRouter(prefix="/state")


@router.post("/lock/{state_id:path}", name="path-convertor", status_code=status.HTTP_200_OK)
async def lock_state(state_id: str, lock_info: types.LockInfo) -> Response:
    """
    Lock the state by its ID.

    The endpoint will return a 423: Locked or 409: Conflict with
    the holding lock info when it's already taken, 200: OK for success.
    """
    try:
        lock.default.lock(
            state_id, lock_info_dict := typing.cast(lock.LockInfo, lock_info.model_dump())
        )
    except lock.AlreadyLocked as err:
        LOG.warning("The lock backend error. %s", str(err), lock_info=lock_info)
        return JSONResponse(err.lock_info, status_code=409)
    except lock.Error as err:
        LOG.error("The lock backend error. %s", str(err))
        raise HTTPException(502, detail=f"Failed to access the {lock.default.name} lock backend.")
    LOG.info("Locked the state.", state_id=state_id, lock_info=lock_info_dict)
    return Response(status_code=200)


@router.post("/unlock/{state_id:path}", name="path-convertor", status_code=status.HTTP_200_OK)
async def unlock_state(state_id: str, request: Request) -> None:
    """
    Unlock the state by its ID.

    The **force-unlock** implementation ignores the lock ID because Terraform
    lacks proper force-unlock functionality for the HTTP backend.
    See [this issue](https://github.com/hashicorp/terraform/issues/28421) for more details.
    As a result, when you run `tofu force-unlock XXX`, Tofu/Terraform does not
    pass the lock ID (`XXX`) to the HTTP backend, causing the backend to skip
    lock ID verification.

    The endpoint will return a 423: Locked or 409: Conflict with
    the holding lock info when it's already taken, 200: OK for success.
    """
    try:
        lock_info_dict = lock.default.unlock(state_id)
    except lock.NotLocked as err:
        LOG.warning("The lock backend error. %s", str(err))
        raise HTTPException(409, detail=f"State with ID {state_id} is not locked.")
    except lock.Error as err:
        LOG.error("The lock backend error. %s", str(err))
        raise HTTPException(502, detail=f"Failed to access the {lock.default.name} lock backend.")

    lock_info = types.LockInfo(**lock_info_dict)  # type: ignore
    LOG.info("Removed lock from the state.", state_id=state_id, **lock_info.model_dump())


@router.get("/{state_id:path}", name="path-convertor")
async def get_state(state_id: str) -> types.TerraformState:
    """Fetch the state by its ID."""
    LOG.info("Fetching state...", state_id=state_id)

    try:
        body = storage.default.get(state_id)
    except storage.NotFound as err:
        LOG.debug("The storage backend not found error. %s", str(err))
        raise HTTPException(404, detail=f"The state with ID {state_id} not found.")
    except storage.Error as err:
        LOG.debug("The storage backend error. %s", str(err))
        raise HTTPException(
            502, detail=f"Failed to access the {storage.default.name} storage backend."
        )

    try:
        state = types.TerraformState(**orjson.loads(body))
    except (ValueError, pydantic_core.ValidationError) as err:
        raise HTTPException(400, detail=f"Cannot decode the state wiith ID {state_id}")
    else:
        LOG.info("Fetched state.", state_id=state_id, lineage=state.lineage, version=state.version)
        return state


@router.post("/{state_id:path}", name="path-convertor")
async def post_state(state_id: str, request: Request) -> None:
    """Create the state by its ID."""
    body = await request.body()
    sha256 = await service.sha256_digest(body)
    size_mb = round(len(body) / (1024 * 1024), 3)

    LOG.info("Creating state...", state_id=state_id, sha256=sha256, size_mb=size_mb)
    try:
        storage.default.create(state_id, body)
    except storage.Error as err:
        LOG.debug("The storage backend error. %s", str(err))
        raise HTTPException(
            502, detail=f"Failed to access the {storage.default.name} storage backend."
        )
    else:
        LOG.info("Created state.", state_id=state_id, sha256=sha256, size_mb=size_mb)


@router.delete("/{state_id:path}", name="path-convertor")
async def delete_state(state_id: str) -> None:
    """Delete the state by its ID."""
    LOG.info("Deleting state...", state_id=state_id)

    try:
        storage.default.delete(state_id)
    except storage.NotFound as err:
        LOG.debug("The storage backend not found error. %s", str(err))
        raise HTTPException(404, detail=f"The state with ID {state_id} not found.")
    except storage.Error as err:
        LOG.debug("The storage backend error. %s", str(err))
        raise HTTPException(
            502, detail=f"Failed to access the {storage.default.name} storage backend."
        )
