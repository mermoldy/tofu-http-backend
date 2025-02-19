from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

__all__ = ["TerraformState"]


class TerraformState(BaseModel):
    """
    Represents the structure of a Terraform state file.

    This includes metadata, resource definitions, outputs, and check results.
    """

    version: int = Field(..., description="State file version.")
    terraform_version: str = Field(..., description="Terraform version used to generate the state.")
    serial: int = Field(..., description="Incrementing number for state revisions.")
    lineage: str = Field(..., description="Unique identifier for this state lineage.")
    outputs: dict[str, dict] = Field(
        default_factory=dict, description="Output values from Terraform."
    )
    resources: list[dict] = Field(default_factory=list, description="List of managed resources.")
    check_results: list[dict] | None = Field(
        description="Results of Terraform checks, if applicable."
    )


class LockInfo(BaseModel):
    """
    Represents a Terraform (or OpenTofu) state lock.

    This lock prevents multiple concurrent operations from modifying the same state.
    """

    id: str = Field(..., alias="ID", description="Unique identifier for the lock.")
    operation: str = Field(
        ...,
        alias="Operation",
        description="The operation being performed (e.g., 'OperationTypeApply').",
    )
    info: str = Field(
        default="", alias="Info", description="Additional information about the lock."
    )
    who: str = Field(
        ..., alias="Who", description="Identifier of the user or process that acquired the lock."
    )
    version: str = Field(
        ..., alias="Version", description="Version of the Terraform/OpenTofu tool used."
    )
    created: datetime = Field(
        ..., alias="Created", description="Timestamp when the lock was created."
    )
    path: str = Field(default="", alias="Path", description="Path to the locked resource.")

    class Config:
        """Configuration for the Pydantic model."""

        populate_by_name = True  # Enables aliasing in serialization & parsing
        json_schema_extra = {
            "example": {
                "ID": "d3d67d5e-6695-2885-c52e-ebf6f5d71c78",
                "Operation": "OperationTypeApply",
                "Info": "",
                "Who": "mermoldy@Serhiis-MacBook-Pro.local",
                "Version": "1.9.0",
                "Created": "2025-02-19T15:47:52.732586Z",
                "Path": "",
            }
        }
