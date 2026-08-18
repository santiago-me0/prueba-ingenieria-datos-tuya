"""
Tests for the data-quality and preparation layer
of Exercise 3.
"""

from pathlib import Path
import sqlite3
import unittest


EXERCISE_DIR = Path(__file__).resolve().parents[1]

SCHEMA_PATH = EXERCISE_DIR / "sql" / "01_schema.sql"
PREPARE_PATH = EXERCISE_DIR / "sql" / "03_prepare_data.sql"


class TestPrepareData(unittest.TestCase):

    def setUp(self) -> None:
        """Create an isolated in-memory SQLite database."""

        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row

        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        self.connection.executescript(schema)

    def tearDown(self) -> None:
        """Close the temporary database."""

        self.connection.close()

    def insert_history(self, rows: list[tuple]) -> None:
        """Insert history rows into the RAW layer."""

        self.connection.executemany(
            """
            INSERT INTO historia_raw (
                identificacion,
                corte_mes,
                saldo
            )
            VALUES (?, ?, ?)
            """,
            rows,
        )

    def insert_retirements(self, rows: list[tuple]) -> None:
        """Insert retirement rows into the RAW layer."""

        self.connection.executemany(
            """
            INSERT INTO retiros_raw (
                identificacion,
                fecha_retiro
            )
            VALUES (?, ?)
            """,
            rows,
        )

    def prepare_data(self) -> None:
        """Execute the real preparation SQL script."""

        sql = PREPARE_PATH.read_text(encoding="utf-8")
        self.connection.executescript(sql)

    def test_exact_duplicate_is_deduplicated(self) -> None:
        """
        Exact customer-month duplicates should become one
        prepared record and be registered in the quality log.
        """

        self.insert_history(
            [
                ("CLIENT_A", "2024-01-31", 500000),
                ("CLIENT_A", "2024-01-31", 500000),
            ]
        )

        self.prepare_data()

        rows = self.connection.execute(
            """
            SELECT *
            FROM historia_prepared
            WHERE identificacion = 'CLIENT_A'
            """
        ).fetchall()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["saldo"], 500000)
        self.assertEqual(
            rows[0]["preparation_status"],
            "DEDUPLICATED_EXACT",
        )

        issue = self.connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM data_quality_issues
            WHERE issue_type = 'EXACT_DUPLICATE'
            """
        ).fetchone()

        self.assertEqual(issue["total"], 1)

    def test_conflicting_balance_uses_max_and_is_quarantined(self) -> None:
        """
        Different balances for the same customer-month should
        be quarantined while MAX(saldo) is used as the
        deterministic fallback in the prepared layer.
        """

        self.insert_history(
            [
                ("CLIENT_A", "2024-01-31", 500000),
                ("CLIENT_A", "2024-01-31", 1500000),
            ]
        )

        self.prepare_data()

        prepared = self.connection.execute(
            """
            SELECT *
            FROM historia_prepared
            WHERE identificacion = 'CLIENT_A'
            """
        ).fetchone()

        self.assertEqual(prepared["saldo"], 1500000)

        self.assertEqual(
            prepared["preparation_status"],
            "CONFLICT_RESOLVED_MAX_BALANCE",
        )

        quarantine = self.connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM historia_quarantine
            WHERE issue_type = 'CONFLICTING_BALANCE'
            """
        ).fetchone()

        self.assertEqual(quarantine["total"], 2)

        issue = self.connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM data_quality_issues
            WHERE issue_type = 'CONFLICTING_BALANCE'
            """
        ).fetchone()

        self.assertEqual(issue["total"], 1)

    def test_post_retirement_records_are_excluded_and_quarantined(
        self,
    ) -> None:
        """
        Monthly cuts after the retirement date must not reach
        the prepared history.
        """

        self.insert_history(
            [
                ("CLIENT_A", "2024-01-31", 1500000),
                ("CLIENT_A", "2024-02-29", 1500000),
                ("CLIENT_A", "2024-03-31", 1500000),
            ]
        )

        self.insert_retirements(
            [
                ("CLIENT_A", "2024-02-15"),
            ]
        )

        self.prepare_data()

        prepared = self.connection.execute(
            """
            SELECT corte_mes
            FROM historia_prepared
            WHERE identificacion = 'CLIENT_A'
            ORDER BY corte_mes
            """
        ).fetchall()

        self.assertEqual(
            [row["corte_mes"] for row in prepared],
            ["2024-01-31"],
        )

        quarantine = self.connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM historia_quarantine
            WHERE issue_type = 'POST_RETIREMENT_RECORD'
            """
        ).fetchone()

        self.assertEqual(quarantine["total"], 2)

    def test_retirement_without_history_is_reported(self) -> None:
        """
        Retirement identifiers without an exact history match
        must be reported without inferring or correcting IDs.
        """

        self.insert_history(
            [
                ("CLIENT_A", "2024-01-31", 500000),
            ]
        )

        self.insert_retirements(
            [
                ("CLIENT_UNKNOWN", "2024-03-15"),
            ]
        )

        self.prepare_data()

        issue = self.connection.execute(
            """
            SELECT
                issue_type,
                resolution
            FROM data_quality_issues
            WHERE identificacion = 'CLIENT_UNKNOWN'
            """
        ).fetchone()

        self.assertIsNotNone(issue)

        self.assertEqual(
            issue["issue_type"],
            "RETIREMENT_WITHOUT_HISTORY",
        )

        self.assertEqual(
            issue["resolution"],
            "NO_MATCH_NO_INFERENCE",
        )


if __name__ == "__main__":
    unittest.main()