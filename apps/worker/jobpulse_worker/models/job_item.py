from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class JobItem(BaseModel):
    """
    Model representing a job posting for ingestion.

    Attributes:
        source: Name of the job source (must match a record in the 'sources' table)
        url: Source URL of the job posting
        title: Job title
        company: Company name
        location: Job location
        description: Optional job description text
        scraped_at: Timestamp when the job was scraped. When deserializing from JSON,
                    Pydantic automatically parses ISO 8601 formatted strings (e.g.,
                    "2024-01-30T12:00:00Z") into datetime objects.
        canonical_hash: Deterministic hash for deduplication (use utils.fingerprint.canonical_hash)
        content_hash: Hash of content fields for versioning (use utils.fingerprint.content_hash)
    """

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
    def _strip_required(cls, value: object, info) -> object:
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                raise ValueError(f"{info.field_name} must not be empty")
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
