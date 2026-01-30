from __future__ import annotations

import os
from typing import Iterable

from psycopg import Connection, connect

from jobpulse_worker.models.job_item import JobItem

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://jobpulse:jobpulse@postgres:5432/jobpulse",
)


def persist_job_items(job_items: Iterable[JobItem]) -> dict[str, int]:
    items = list(job_items)
    if not items:
        return {"processed": 0, "jobs_upserted": 0, "versions_inserted": 0}

    source_cache: dict[str, int] = {}
    jobs_upserted = 0
    versions_inserted = 0

    with connect(DATABASE_URL) as conn:
        with conn.transaction():
            for item in items:
                source_id = _get_source_id(conn, item.source, source_cache)
                job_id = _upsert_job(conn, source_id, item)
                jobs_upserted += 1
                if _insert_job_version(conn, job_id, item):
                    versions_inserted += 1

    return {
        "processed": len(items),
        "jobs_upserted": jobs_upserted,
        "versions_inserted": versions_inserted,
    }


def _get_source_id(
    conn: Connection,
    source_name: str,
    cache: dict[str, int],
) -> int:
    cached = cache.get(source_name)
    if cached is not None:
        return cached

    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
        row = cursor.fetchone()

    if row is None:
        raise ValueError(f"source_not_found: {source_name}")

    source_id = int(row[0])
    cache[source_name] = source_id
    return source_id


def _upsert_job(conn: Connection, source_id: int, item: JobItem) -> int:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO jobs (
                source_id,
                source_job_id,
                source_url,
                canonical_hash,
                first_seen_at,
                last_seen_at
            )
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (source_id, canonical_hash)
            DO UPDATE SET last_seen_at = EXCLUDED.last_seen_at
            RETURNING id;
            """,
            (
                source_id,
                None,
                item.url,
                item.canonical_hash,
            ),
        )
        row = cursor.fetchone()

    if row is None:
        raise RuntimeError("job_upsert_failed")
    return int(row[0])


def _insert_job_version(conn: Connection, job_id: int, item: JobItem) -> bool:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO job_versions (
                job_id,
                title,
                company,
                location,
                description,
                scraped_at,
                content_hash
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (job_id, content_hash) DO NOTHING
            RETURNING id;
            """,
            (
                job_id,
                item.title,
                item.company,
                item.location,
                item.description,
                item.scraped_at,
                item.content_hash,
            ),
        )
        row = cursor.fetchone()

    return row is not None
