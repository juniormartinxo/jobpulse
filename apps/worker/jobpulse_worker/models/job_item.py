from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class JobItem(BaseModel):
    source: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    description: str | None = None
    scraped_at: datetime
    canonical_hash: str = Field(..., min_length=1)
    content_hash: str = Field(..., min_length=1)

    @field_validator(
        "source",
        "url",
        "title",
        "company",
        "location",
        "canonical_hash",
        "content_hash",
        mode="before",
    )
    @classmethod
    def _strip_required(cls, value: object) -> object:
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                raise ValueError("value must not be empty")
            return cleaned
        return value

    @field_validator("description", mode="before")
    @classmethod
    def _strip_description(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned or None
        return value
