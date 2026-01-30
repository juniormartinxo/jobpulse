from __future__ import annotations

import hashlib
from typing import Iterable


def _normalize_identity(value: str) -> str:
    return " ".join(value.split()).strip().lower()


def _normalize_content(value: str) -> str:
    return " ".join(value.split()).strip()


def _hash_parts(parts: Iterable[str]) -> str:
    payload = "\u001f".join(parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonical_hash(source: str, title: str, company: str, location: str) -> str:
    parts = [
        _normalize_identity(source),
        _normalize_identity(title),
        _normalize_identity(company),
        _normalize_identity(location),
    ]
    return _hash_parts(parts)


def content_hash(
    *,
    source: str,
    url: str,
    title: str,
    company: str,
    location: str,
    description: str | None,
) -> str:
    parts = [
        _normalize_content(source),
        _normalize_content(url),
        _normalize_content(title),
        _normalize_content(company),
        _normalize_content(location),
        _normalize_content(description or ""),
    ]
    return _hash_parts(parts)
