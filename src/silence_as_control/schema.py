"""API schemas for control-layer requests and responses."""

from typing import Literal, Union

from pydantic import BaseModel, Field

from silence_as_control.config import (
    CONTROL_MAX_DRIFT_DEFAULT,
    CONTROL_MIN_COHERENCE_DEFAULT,
)


class GenerateRequest(BaseModel):
    output: str
    coherence: float
    drift: float
    threshold: float = Field(default=CONTROL_MIN_COHERENCE_DEFAULT)
    tolerance: float = Field(default=CONTROL_MAX_DRIFT_DEFAULT)


class OkResponse(BaseModel):
    status: Literal["ok"]
    output: str


class AbstainedResponse(BaseModel):
    status: Literal["abstained"]
    reason: Literal["control_abstention"]


GenerateResponse = Union[OkResponse, AbstainedResponse]
