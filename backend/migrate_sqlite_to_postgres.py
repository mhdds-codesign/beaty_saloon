"""Copy the five Beauty Salon application tables from local SQLite to Supabase PostgreSQL.

Run from the backend directory after setting DATABASE_URL to the Supabase
PostgreSQL connection string:

    python migrate_sqlite_to_postgres.py --sqlite ./saloon.db

The script preserves primary keys and password hashes. By default it refuses
to write if the destination application tables already contain data.
Use --replace only when you intentionally want to clear those five tables.
"""
import argparse
from pathlib import Path

from sqlalchemy import MetaData, create_engine, delete, func, insert, select, text
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, engine as target_engine
# Register all ORM models on Base.metadata before creating or inspecting tables.
from app.models import Admin, Customer, Line, Reservation, WorkSchedule  # noqa: F401

TABLE_ORDER = [
    "customers",
    "lines",
    "work_schedules",
    "admins",
    "reservations",
]
TABLE_DELETE_ORDER = list(reversed(TABLE_ORDER))


def main():
    parser = argparse.ArgumentParser(description="Migrate local SQLite data to PostgreSQL.")
    parser.add_argument(
        "--sqlite",
        default=str(Path(__file__).resolve().parent / "saloon.db"),
        help="Path to the source SQLite file (default: backend/saloon.db).",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Clear the five destination application tables before importing.",
    )
    args = parser.parse_args()

    sqlite_path = Path(args.sqlite).expanduser().resolve()
    if not sqlite_path.is_file():
        raise SystemExit(f"SQLite file not found: {sqlite_path}")

    if target_engine.dialect.name != "postgresql":
        raise SystemExit(
            "DATABASE_URL must point to Supabase PostgreSQL. "
            "Do not run this script with the local SQLite fallback."
        )

    source_engine = create_engine(f"sqlite:///{sqlite_path.as_posix()}")
    source_metadata = MetaData()
    source_metadata.reflect(bind=source_engine)

    required_missing = [name for name in TABLE_ORDER if name not in source_metadata.tables]
    if required_missing:
        source_engine.dispose()
        raise SystemExit(
            "The SQLite file is missing expected application tables: "
            + ", ".join(required_missing)
        )

    # Create destination tables from the current SQLAlchemy models.
    Base.metadata.create_all(bind=target_engine)
    target_metadata = Base.metadata

    try:
        # Keep the SQLite connection open during the whole copy operation.
        with source_engine.connect() as source_conn:
            source_counts = {
                name: source_conn.scalar(
                    select(func.count()).select_from(source_metadata.tables[name])
                )
                for name in TABLE_ORDER
            }

            print("Source SQLite rows:")
            for name in TABLE_ORDER:
                print(f"  {name}: {source_counts[name]}")

            with target_engine.begin() as target_conn:
                target_counts = {
                    name: target_conn.scalar(
                        select(func.count()).select_from(target_metadata.tables[name])
                    )
                    for name in TABLE_ORDER
                }

                if any(target_counts.values()) and not args.replace:
                    details = ", ".join(
                        f"{name}={count}" for name, count in target_counts.items()
                    )
                    raise SystemExit(
                        "Destination is not empty (" + details + "). "
                        "Nothing was imported. Use --replace only if clearing it is intended."
                    )

                if args.replace:
                    for name in TABLE_DELETE_ORDER:
                        target_conn.execute(delete(target_metadata.tables[name]))

                for name in TABLE_ORDER:
                    source_table = source_metadata.tables[name]
                    target_table = target_metadata.tables[name]
                    target_columns = {column.name for column in target_table.columns}
                    source_columns = {column.name for column in source_table.columns}
                    common_columns = [
                        column.name for column in target_table.columns
                        if column.name in source_columns
                    ]

                    rows = source_conn.execute(select(source_table)).mappings()
                    batch = []
                    imported = 0
                    for source_row in rows:
                        row = {column: source_row[column] for column in common_columns}
                        # Very old SQLite databases may predate role/customer_id.
                        if name == "admins":
                            if "role" in target_columns and "role" not in source_columns:
                                row["role"] = "admin"
                            if "customer_id" in target_columns and "customer_id" not in source_columns:
                                row["customer_id"] = None
                        batch.append(row)

                        if len(batch) >= 500:
                            target_conn.execute(insert(target_table), batch)
                            imported += len(batch)
                            batch.clear()

                    if batch:
                        target_conn.execute(insert(target_table), batch)
                        imported += len(batch)

                    print(f"Imported {name}: {imported} rows")

                # Advance PostgreSQL sequences after preserving SQLite IDs.
                for name in TABLE_ORDER:
                    if "id" in target_metadata.tables[name].columns:
                        target_conn.execute(
                            text(
                                f"SELECT setval(pg_get_serial_sequence('{name}', 'id'), "
                                f"COALESCE((SELECT MAX(id) FROM {name}), 1), "
                                f"(SELECT COUNT(*) FROM {name}) > 0)"
                            )
                        )

        print("Migration completed successfully.")
    except SystemExit:
        raise
    except SQLAlchemyError as exc:
        raise SystemExit(f"Migration failed and was rolled back: {exc}") from exc
    finally:
        source_engine.dispose()


if __name__ == "__main__":
    main()
