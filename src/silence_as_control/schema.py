"""API schemas for control-layer requests and responses."""

from typing import Literal, Union

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    output: str
    coherence: float
    drift: float
    threshold: float = Field(default=0.7)
    tolerance: float = Field(default=0.3)


class OkResponse(BaseModel):
    status: Literal["ok"]
    output: str


class AbstainedResponse(BaseModel):
    status: Literal["abstained"]
    reason: Literal["control_abstention"]


GenerateResponse = Union[OkResponse, AbstainedResponse]
