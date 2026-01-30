from __future__ import annotations

import os
from typing import Iterable

from psycopg import Connection
from psycopg_pool import ConnectionPool

from jobpulse_worker.models.job_item import JobItem

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://jobpulse:jobpulse@postgres:5432/jobpulse",
)

# Connection pool for production workloads with high throughput
_connection_pool: ConnectionPool | None = None


def _get_connection_pool() -> ConnectionPool:
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            open=True,
        )
    return _connection_pool


def close_connection_pool() -> None:
    """Close the connection pool. Should be called on worker shutdown."""
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.close()
        _connection_pool = None


def persist_job_items(job_items: Iterable[JobItem]) -> dict[str, int]:
    items = list(job_items)
    if not items:
        return {"processed": 0, "jobs_upserted": 0, "versions_inserted": 0}

    source_cache: dict[str, int] = {}
    jobs_upserted = 0
    versions_inserted = 0

    pool = _get_connection_pool()
    with pool.connection() as conn:
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
        raise ValueError(
            f"source_not_found: {source_name}. "
            "Source records must be pre-populated in the 'sources' table before ingesting jobs."
        )

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
            DO UPDATE SET
                last_seen_at = EXCLUDED.last_seen_at,
                source_job_id = COALESCE(EXCLUDED.source_job_id, jobs.source_job_id),
                source_url = COALESCE(EXCLUDED.source_url, jobs.source_url)
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

    # This check should never fail as UPSERT always returns a row (inserted or updated).
    # Kept as a safety guard for unexpected database states.
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
