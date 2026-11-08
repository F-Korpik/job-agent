from typing import Literal
from pydantic import BaseModel, Field


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
    tags: list[str] = Field(default_factory=list)
    url: str | None = None
    portal: str = "justjoin.it"