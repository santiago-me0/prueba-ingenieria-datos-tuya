"""
Execute the streak query for Exercise 3.

The query is parameterized by:

    fecha_base: historical analysis date (YYYY-MM-DD)
    n: minimum streak length

Example:

    python -m Ejercicio_3.src.run_query \
        --fecha-base 2024-12-31 \
        --n 3
"""

from argparse import ArgumentParser
from datetime import date
from pathlib import Path
import sqlite3


EXERCISE_DIR = Path(__file__).resolve().parents[1]

DATABASE_PATH = EXERCISE_DIR / "rachas.db"
QUERY_PATH = EXERCISE_DIR / "sql" / "04_rachas.sql"


def validate_date(value: str) -> str:
    """Validate an ISO date in YYYY-MM-DD format."""

    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            "fecha_base must use YYYY-MM-DD format."
        ) from exc

    return value


def validate_n(value: int) -> int:
    """Validate the minimum streak length."""

    if value < 1:
        raise ValueError(
            "n must be greater than or equal to 1."
        )

    return value


def print_results(rows: list[sqlite3.Row]) -> None:
    """Print query results as a formatted table."""

    if not rows:
        print("No streaks found for the specified parameters.")
        return

    columns = [
        "identificacion",
        "racha",
        "fecha_fin",
        "nivel",
    ]

    widths = {
        column: max(
            len(column),
            max(len(str(row[column])) for row in rows),
        )
        for column in columns
    }

    header = " | ".join(
        column.ljust(widths[column])
        for column in columns
    )

    separator = "-+-".join(
        "-" * widths[column]
        for column in columns
    )

    print(header)
    print(separator)

    for row in rows:
        print(
            " | ".join(
                str(row[column]).ljust(widths[column])
                for column in columns
            )
        )


def run_query(
    fecha_base: str,
    n: int,
) -> list[sqlite3.Row]:
    """Execute the streak calculation."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Run the data-loading process first:\n"
            "python -m Ejercicio_3.src.load_data"
        )

    if not QUERY_PATH.exists():
        raise FileNotFoundError(
            f"SQL query not found: {QUERY_PATH}"
        )

    fecha_base = validate_date(fecha_base)
    n = validate_n(n)

    query = QUERY_PATH.read_text(
        encoding="utf-8"
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            query,
            {
                "fecha_base": fecha_base,
                "n": n,
            },
        ).fetchall()

    return rows


def main() -> None:
    """CLI entry point."""

    parser = ArgumentParser(
        description=(
            "Calculate customer balance streaks "
            "for a historical base date."
        )
    )

    parser.add_argument(
        "--fecha-base",
        required=True,
        help="Historical analysis date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--n",
        required=True,
        type=int,
        help="Minimum number of consecutive months.",
    )

    args = parser.parse_args()

    try:
        rows = run_query(
            fecha_base=args.fecha_base,
            n=args.n,
        )
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))

    print()
    print(f"fecha_base: {args.fecha_base}")
    print(f"n: {args.n}")
    print(f"customers selected: {len(rows)}")
    print()

    print_results(rows)


if __name__ == "__main__":
    main()