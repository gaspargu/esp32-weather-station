"""Validation schemas for incoming and stored sensor readings."""

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class ReadingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    device_id: str = Field(min_length=1, max_length=64)
    temperature_c: float = Field(ge=-40, le=80, allow_inf_nan=False)
    humidity_pct: float = Field(ge=0, le=100, allow_inf_nan=False)
    measured_at: AwareDatetime | None = None


class Reading(ReadingCreate):
    id: int
    received_at: AwareDatetime
