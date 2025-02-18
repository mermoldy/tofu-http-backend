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
