"""The HTTP state API routes."""

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from src import log
from src import storage

from . import types

LOG = log.get_logger(__name__)

router = APIRouter(prefix="/state")


@router.get("/{state_id:path}", name="path-convertor")
async def get_state(state_id: str) -> dict:
    """Fetch the state by its ID."""
    LOG.info("Fetching state.", state_id=state_id)

    try:
        blob = storage.default.get(state_id)
    except storage.NotFound as err:
        LOG.info("The storage backend error. %s", str(err))
        raise HTTPException(status_code=404, detail=f"The state with ID {state_id} not found.")

    LOG.info("Test")
    return {"message": "Hello World"}


@router.post("/{state_id:path}", name="path-convertor")
async def post_state(state_id: str, state: types.TerraformState) -> dict:
    """Create the state by its ID."""
    LOG.info("Creating state.", state_id=state_id, state=state)

    storage_client = storage.get_client()
    obj = storage_client.get_object("http_states", state_id)

    raise HTTPException(status_code=404, detail="State not found")

    return {"message": "Hello World"}


@router.delete("/{state_id:path}", name="path-convertor")
async def delete_state(state_id: str) -> dict:
    """Delete the state by its ID."""
    LOG.info("Deleting state.", state_id=state_id, state=state)

    raise HTTPException(status_code=404, detail="State not found")

    LOG.info("Test")
    c = storage.get_client()
    return {"message": "Hello World"}


@router.delete("/{state_id:path}/lock", name="path-convertor")
async def lock_state(state_id: str) -> dict:
    """Lock the state by its ID."""
    raise HTTPException(status_code=404, detail="State not found")


@router.delete("/{state_id:path}/unlock", name="path-convertor")
async def unlock_state(state_id: str) -> dict:
    """Unlock the state by its ID."""
    raise HTTPException(status_code=404, detail="State not found")
