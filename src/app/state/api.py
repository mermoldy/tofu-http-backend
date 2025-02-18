"""The HTTP state API routes."""

import orjson
import pydantic_core
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from src import log
from src import storage

from . import service
from . import types

LOG = log.get_logger(__name__)

router = APIRouter(prefix="/state")


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
            503, detail=f"Failed to access the {storage.default.name} storage backend."
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

    LOG.info("Creating state...", state_id=state_id, sha256=sha256)
    try:
        storage.default.create(state_id, body)
    except storage.Error as err:
        LOG.debug("The storage backend error. %s", str(err))
        raise HTTPException(
            503, detail=f"Failed to access the {storage.default.name} storage backend."
        )
    else:
        LOG.info("Created state.", state_id=state_id, sha256=sha256)


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
            503, detail=f"Failed to access the {storage.default.name} storage backend."
        )


@router.delete("/{state_id:path}/lock", name="path-convertor")
async def lock_state(state_id: str) -> dict:
    """
    Lock the state by its ID.

    The endpoint will return a 423: Locked or 409: Conflict with
    the holding lock info when it's already taken, 200: OK for success.
    """
    raise HTTPException(status_code=404, detail="State not found")


@router.delete("/{state_id:path}/unlock", name="path-convertor")
async def unlock_state(state_id: str) -> dict:
    """
    Unlock the state by its ID.

    The endpoint will return a 423: Locked or 409: Conflict with
    the holding lock info when it's already taken, 200: OK for success.
    """
    raise HTTPException(status_code=404, detail="State not found")
