from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Offer(BaseModel):
    title: str
    company: str
    location: str | None = None
    work_mode: Literal["remote", "hybrid", "office"] | None = None
    contract_types: list[str] = Field(default_factory=list)
    level: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    currency: str | None = None
    salary_period: Literal["month", "year", "hour"] | None = None
    tags: list[str] = Field(default_factory=list)
    url: str | None = None
    portal: str = "justjoin.it"
    grounded: bool | None = None

    @field_validator("work_mode", "salary_period", mode="before")
    @classmethod
    def _lowercase(cls, value):
        return value.lower() if isinstance(value, str) else value