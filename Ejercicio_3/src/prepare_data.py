"""
Prepare Exercise 3 data for streak calculation.

This module executes the data-quality and preparation layer
after the RAW source data has been loaded into SQLite.
"""

from pathlib import Path
import sqlite3


EXERCISE_DIR = Path(__file__).resolve().parents[1]

DATABASE_PATH = EXERCISE_DIR / "rachas.db"
PREPARE_SQL_PATH = EXERCISE_DIR / "sql" / "03_prepare_data.sql"


def prepare_data() -> None:
    """Execute the preparation and quarantine SQL script."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Run the data-loading process first:\n"
            "python -m Ejercicio_3.src.load_data"
        )

    sql = PREPARE_SQL_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(sql)
        connection.commit()


def main() -> None:
    """CLI entry point."""

    prepare_data()

    print("Data prepared successfully.")
    print(f"Database: {DATABASE_PATH}")


if __name__ == "__main__":
    main()