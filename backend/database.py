"""
PostgreSQL-backed sharded database using consistent hashing.

Each shard maps to a dedicated PostgreSQL schema (shard_1 … shard_4).
Write operations use 2-replica writes; reads include read-repair via updated_at.
"""

import json
import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
import psycopg2.extras

from consistent_hash import ring, SHARD_NAMES

# ── Connection config ─────────────────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = int(os.getenv("DB_PORT", "5432"))
DB_NAME     = os.getenv("DB_NAME",     "unc_resource_engine")
DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def _schema(shard: str) -> str:
    """'shard-1' → 'shard_1'  (hyphens are not valid in PG schema names)."""
    return shard.replace("-", "_")


@contextmanager
def _conn(shard: str):
    """Context manager: open a connection scoped to the shard's schema."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        options=f"-c search_path={_schema(shard)},public",
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Internal write / read ─────────────────────────────────────────────────────

def _put(resource_id: str, value: Any) -> List[str]:
    """Write to primary + one replica (2-replica write). Returns written shards."""
    replicas = ring.get_replicas(resource_id, n=2)
    res_type = resource_id.split(":")[0]
    data_json = json.dumps(value)

    for shard in replicas:
        with _conn(shard) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO resources (id, type, data, updated_at)
                    VALUES (%s, %s, %s::jsonb, NOW())
                    ON CONFLICT (id) DO UPDATE
                        SET data       = EXCLUDED.data,
                            updated_at = NOW()
                    """,
                    (resource_id, res_type, data_json),
                )
    return replicas


def _fetch_row(shard: str, resource_id: str) -> Optional[dict]:
    """Return the raw DB row {data, updated_at} or None."""
    with _conn(shard) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT data, updated_at FROM resources WHERE id = %s",
                (resource_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None


def _get(resource_id: str) -> Tuple[Optional[Any], str]:
    """
    Read from primary shard with read-repair.
    If a replica has a fresher updated_at, it heals the primary.
    Returns (value_dict, primary_shard_name).
    """
    primary  = ring.get_node(resource_id)
    replicas = ring.get_replicas(resource_id, n=2)

    primary_row = _fetch_row(primary, resource_id)
    best_row    = primary_row
    best_ts     = primary_row["updated_at"] if primary_row else None

    for shard in replicas:
        if shard == primary:
            continue
        row = _fetch_row(shard, resource_id)
        if row and (best_ts is None or row["updated_at"] > best_ts):
            best_row = row
            best_ts  = row["updated_at"]

    # Repair primary if we found fresher data elsewhere
    if best_row and best_row is not primary_row:
        with _conn(primary) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO resources (id, type, data, updated_at)
                    VALUES (%s, %s, %s::jsonb, %s)
                    ON CONFLICT (id) DO UPDATE
                        SET data       = EXCLUDED.data,
                            updated_at = EXCLUDED.updated_at
                    """,
                    (
                        resource_id,
                        resource_id.split(":")[0],
                        json.dumps(dict(best_row["data"])),
                        best_ts,
                    ),
                )

    value = dict(best_row["data"]) if best_row else None
    return value, primary


def _list_by_type(resource_type: str) -> Tuple[List[Any], Dict[str, int]]:
    """Return all unique records of a given type plus per-shard counts."""
    seen_ids:    set            = set()
    unique:      List[Any]      = []
    shard_counts: Dict[str, int] = {s: 0 for s in SHARD_NAMES}

    for shard in SHARD_NAMES:
        with _conn(shard) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, data FROM resources WHERE type = %s",
                    (resource_type,),
                )
                rows = cur.fetchall()
                shard_counts[shard] = len(rows)
                for row in rows:
                    if row["id"] not in seen_ids:
                        seen_ids.add(row["id"])
                        unique.append(dict(row["data"]))

    return unique, shard_counts


# ── Public API ────────────────────────────────────────────────────────────────

def get_resource(
    resource_type: str, resource_id: str
) -> Tuple[Optional[dict], str, List[str]]:
    """Returns (item, primary_shard, replica_shards)."""
    key      = f"{resource_type}:{resource_id}"
    value, primary = _get(key)
    replicas = ring.get_replicas(key, n=2)
    return value, primary, replicas


def list_resources(resource_type: str) -> Tuple[List[dict], Dict[str, int]]:
    return _list_by_type(resource_type)


def search_all(query: str) -> List[dict]:
    query_lower = query.lower()
    results: List[dict] = []
    seen_ids: set = set()

    for resource_type in ["course", "club", "research", "event", "dining"]:
        items, _ = _list_by_type(resource_type)
        for item in items:
            item_id = item.get("id", "")
            if item_id in seen_ids:
                continue
            if query_lower in " ".join(str(v) for v in item.values()).lower():
                seen_ids.add(item_id)
                results.append({"type": resource_type, **item})

    return results


def get_shard_distribution() -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for shard in SHARD_NAMES:
        with _conn(shard) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM resources")
                counts[shard] = cur.fetchone()[0]
    return counts