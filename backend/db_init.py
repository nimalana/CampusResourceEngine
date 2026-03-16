"""
Initialize PostgreSQL for the UNC Resource Engine.

Creates the database (if needed), 4 shard schemas, the resources table
in each schema, then seeds all UNC data. Safe to re-run — all ops are
idempotent.

Usage:
    python db_init.py
"""

import json
import os
import sys

import psycopg2
from psycopg2 import sql

from consistent_hash import ring, SHARD_NAMES
from seed_data import COURSES, CLUBS, RESEARCH, EVENTS, DINING

DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = int(os.getenv("DB_PORT", "5432"))
DB_NAME     = os.getenv("DB_NAME",     "unc_resource_engine")
DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def _schema(shard: str) -> str:
    return shard.replace("-", "_")


def _admin_conn(dbname: str = "postgres"):
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=dbname,
        user=DB_USER, password=DB_PASSWORD,
    )
    conn.autocommit = True
    return conn


def create_database():
    """Create the application database if it does not exist."""
    conn = _admin_conn("postgres")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            if not cur.fetchone():
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
                print(f"  Created database '{DB_NAME}'")
            else:
                print(f"  Database '{DB_NAME}' already exists")
    finally:
        conn.close()


def create_schemas_and_tables():
    """Create one schema + resources table per shard."""
    conn = _admin_conn(DB_NAME)
    try:
        with conn.cursor() as cur:
            for shard in SHARD_NAMES:
                schema = _schema(shard)
                cur.execute(
                    sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema))
                )
                cur.execute(
                    sql.SQL("""
                        CREATE TABLE IF NOT EXISTS {schema}.resources (
                            id         TEXT        PRIMARY KEY,
                            type       TEXT        NOT NULL,
                            data       JSONB       NOT NULL,
                            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                    """).format(schema=sql.Identifier(schema))
                )
                cur.execute(
                    sql.SQL(
                        "CREATE INDEX IF NOT EXISTS {idx} ON {schema}.resources (type)"
                    ).format(
                        idx=sql.Identifier(f"idx_{schema}_type"),
                        schema=sql.Identifier(schema),
                    )
                )
                print(f"  Schema '{schema}' ready")
    finally:
        conn.close()


def seed_data():
    """Write all seed records through the consistent-hash ring (2-replica writes)."""
    # Import here so database.py picks up the env vars already set
    from database import _put

    datasets = [
        ("course",   COURSES),
        ("club",     CLUBS),
        ("research", RESEARCH),
        ("event",    EVENTS),
        ("dining",   DINING),
    ]

    total = 0
    for resource_type, items in datasets:
        for item in items:
            _put(f"{resource_type}:{item['id']}", item)
            total += 1
        print(f"  Seeded {len(items):>2} {resource_type} records")

    print(f"  {total} records written (×2 replicas = {total * 2} total rows across shards)")


def init_db():
    print("==> Creating database …")
    create_database()

    print("==> Creating schemas and tables …")
    create_schemas_and_tables()

    print("==> Seeding data …")
    seed_data()

    print("==> Done.")


if __name__ == "__main__":
    init_db()
