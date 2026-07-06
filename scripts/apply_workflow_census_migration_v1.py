#!/usr/bin/env python3
"""Apply workflow_census_v1 Supabase migration via NOETFIELD_SUPABASE_DATABASE_URL."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "infrastructure/supabase/migrations/001_workflow_census_v1.sql"
ENV_FILE = Path.home() / ".sourcea-secrets/noetfield-db.env"


def load_database_url() -> str:
    url = os.environ.get("NOETFIELD_SUPABASE_DATABASE_URL", "")
    if url:
        return url.strip()
    if not ENV_FILE.is_file():
        raise SystemExit(f"missing {ENV_FILE}")
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("NOETFIELD_SUPABASE_DATABASE_URL="):
            return line.split("=", 1)[1].strip().strip("'").strip('"')
    raise SystemExit("NOETFIELD_SUPABASE_DATABASE_URL not found in env file")


async def main() -> int:
    try:
        import asyncpg
    except ImportError:
        print("apply_workflow_census_migration_v1: install asyncpg", file=sys.stderr)
        return 1

    sql = MIGRATION.read_text(encoding="utf-8")
    url = load_database_url()
    conn = await asyncpg.connect(url)
    try:
        await conn.execute(sql)
        print("apply_workflow_census_migration_v1: OK")
        print(f"  migration={MIGRATION.relative_to(ROOT)}")
        return 0
    finally:
        await conn.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
