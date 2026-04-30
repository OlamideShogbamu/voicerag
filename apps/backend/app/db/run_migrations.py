import asyncio
import glob
import os

import asyncpg


async def run_migrations():
    print("Starting database migrations...")

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL environment variable is not set")
        raise SystemExit(1)

    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database.")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        raise SystemExit(1)

    try:
        # Use schema-qualified name (public._migrations) so that migrations which
        # call `set_config('search_path', '', false)` don't hide this table.
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS public._migrations (
                id SERIAL PRIMARY KEY,
                filename TEXT UNIQUE,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        migration_dir = os.path.join(os.path.dirname(__file__), "migrations")
        sql_files = sorted(glob.glob(os.path.join(migration_dir, "*.sql")))

        if not sql_files:
            print("No migration files found.")
            return

        for sql_file in sql_files:
            filename = os.path.basename(sql_file)

            already_applied = await conn.fetchval(
                "SELECT id FROM public._migrations WHERE filename = $1", filename
            )

            if already_applied:
                print(f"  skip  {filename} (already applied)")
                continue

            print(f"  apply {filename}")
            with open(sql_file, "r") as f:
                sql = f.read()

            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute(
                    "INSERT INTO public._migrations (filename) VALUES ($1)", filename
                )
            print(f"  done  {filename}")

    finally:
        await conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    asyncio.run(run_migrations())
