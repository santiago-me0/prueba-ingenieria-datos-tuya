"""
Business-rule tests for the streak calculation
of Exercise 3.

The tests execute the real SQL scripts using an isolated
in-memory SQLite database.
"""

from pathlib import Path
import sqlite3
import unittest


EXERCISE_DIR = Path(__file__).resolve().parents[1]

SCHEMA_PATH = EXERCISE_DIR / "sql" / "01_schema.sql"
PREPARE_PATH = EXERCISE_DIR / "sql" / "03_prepare_data.sql"
RACHAS_PATH = EXERCISE_DIR / "sql" / "04_rachas.sql"


class TestRachas(unittest.TestCase):

    def run_streaks(
        self,
        history: list[tuple],
        retirements: list[tuple] | None = None,
        fecha_base: str = "2024-12-31",
        n: int = 1,
    ) -> list[dict]:
        """
        Build an isolated database and execute the real
        preparation and streak SQL.
        """

        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row

        try:
            schema = SCHEMA_PATH.read_text(encoding="utf-8")
            connection.executescript(schema)

            connection.executemany(
                """
                INSERT INTO historia_raw (
                    identificacion,
                    corte_mes,
                    saldo
                )
                VALUES (?, ?, ?)
                """,
                history,
            )

            if retirements:
                connection.executemany(
                    """
                    INSERT INTO retiros_raw (
                        identificacion,
                        fecha_retiro
                    )
                    VALUES (?, ?)
                    """,
                    retirements,
                )

            prepare_sql = PREPARE_PATH.read_text(
                encoding="utf-8"
            )

            connection.executescript(prepare_sql)

            streak_sql = RACHAS_PATH.read_text(
                encoding="utf-8"
            )

            rows = connection.execute(
                streak_sql,
                {
                    "fecha_base": fecha_base,
                    "n": n,
                },
            ).fetchall()

            return [
                dict(row)
                for row in rows
            ]

        finally:
            connection.close()

    @staticmethod
    def get_customer(
        rows: list[dict],
        customer_id: str,
    ) -> dict | None:
        """Find one customer in the result."""

        return next(
            (
                row
                for row in rows
                if row["identificacion"] == customer_id
            ),
            None,
        )

    def test_missing_month_becomes_n0_and_breaks_streak(
        self,
    ) -> None:
        """
        A missing month after the customer's first appearance
        must become N0 and therefore break an existing N2 streak.
        """

        rows = self.run_streaks(
            history=[
                ("CLIENT_A", "2024-01-31", 1500000),  # N2
                ("CLIENT_A", "2024-02-29", 1500000),  # N2
                # March missing -> N0
                ("CLIENT_A", "2024-04-30", 1500000),  # N2
            ],
            fecha_base="2024-04-30",
            n=2,
        )

        result = self.get_customer(
            rows,
            "CLIENT_A",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["racha"], 2)
        self.assertEqual(result["nivel"], "N2")
        self.assertEqual(
            result["fecha_fin"],
            "2024-02-29",
        )

    def test_missing_months_can_form_n0_streak(
        self,
    ) -> None:
        """
        Consecutive missing months after first appearance
        should form an N0 streak.
        """

        rows = self.run_streaks(
            history=[
                ("CLIENT_A", "2024-01-31", 500000),  # N1
                # February missing -> N0
                # March missing -> N0
                ("CLIENT_A", "2024-04-30", 500000),  # N1
            ],
            fecha_base="2024-04-30",
            n=2,
        )

        result = self.get_customer(
            rows,
            "CLIENT_A",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["racha"], 2)
        self.assertEqual(result["nivel"], "N0")
        self.assertEqual(
            result["fecha_fin"],
            "2024-03-31",
        )

    def test_months_before_first_appearance_are_not_imputed(
        self,
    ) -> None:
        """
        N0 should only be generated after the first appearance
        of a customer, never before it.
        """

        rows = self.run_streaks(
            history=[
                # Establish source horizon from January.
                ("CONTROL", "2024-01-31", 500000),
                ("CONTROL", "2024-04-30", 500000),

                # CLIENT_A first appears in March.
                ("CLIENT_A", "2024-03-31", 500000),
                ("CLIENT_A", "2024-04-30", 500000),
            ],
            fecha_base="2024-04-30",
            n=2,
        )

        result = self.get_customer(
            rows,
            "CLIENT_A",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["racha"], 2)
        self.assertEqual(result["nivel"], "N1")
        self.assertEqual(
            result["fecha_fin"],
            "2024-04-30",
        )

    def test_retirement_stops_future_n0_imputation(
        self,
    ) -> None:
        """
        Missing months after a retirement date must not become
        N0 months.
        """

        rows = self.run_streaks(
            history=[
                ("CLIENT_A", "2024-01-31", 500000),
                ("CLIENT_A", "2024-02-29", 500000),

                # CONTROL extends the source horizon.
                ("CONTROL", "2024-01-31", 500000),
                ("CONTROL", "2024-05-31", 500000),
            ],
            retirements=[
                ("CLIENT_A", "2024-03-15"),
            ],
            fecha_base="2024-05-31",
            n=2,
        )

        result = self.get_customer(
            rows,
            "CLIENT_A",
        )

        self.assertIsNotNone(result)

        # Jan-Feb = two consecutive N1 months.
        # Mar-May must NOT be generated as N0.
        self.assertEqual(result["racha"], 2)
        self.assertEqual(result["nivel"], "N1")
        self.assertEqual(
            result["fecha_fin"],
            "2024-02-29",
        )

    def test_fecha_base_excludes_future_monthly_cut(
        self,
    ) -> None:
        """
        If fecha_base is not month-end, only monthly cuts less
        than or equal to fecha_base can participate.
        """

        rows = self.run_streaks(
            history=[
                ("CLIENT_A", "2024-01-31", 1500000),
                ("CLIENT_A", "2024-02-29", 1500000),
                ("CLIENT_A", "2024-03-31", 1500000),
                ("CLIENT_A", "2024-04-30", 3500000),
            ],
            fecha_base="2024-03-15",
            n=2,
        )

        result = self.get_customer(
            rows,
            "CLIENT_A",
        )

        self.assertIsNotNone(result)

        # March 31 is after March 15 and cannot participate.
        self.assertEqual(result["racha"], 2)
        self.assertEqual(result["nivel"], "N2")
        self.assertEqual(
            result["fecha_fin"],
            "2024-02-29",
        )

    def test_longest_eligible_streak_is_selected(
        self,
    ) -> None:
        """
        When several streaks satisfy n, the longest one must
        be selected.
        """

        rows = self.run_streaks(
            history=[
                ("CLIENT_A", "2024-01-31", 500000),   # N1
                ("CLIENT_A", "2024-02-29", 500000),   # N1

                ("CLIENT_A", "2024-03-31", 1500000),  # N2

                ("CLIENT_A", "2024-04-30", 500000),   # N1
                ("CLIENT_A", "2024-05-31", 500000),   # N1
                ("CLIENT_A", "2024-06-30", 500000),   # N1
            ],
            fecha_base="2024-06-30",
            n=2,
        )

        result = self.get_customer(
            rows,
            "CLIENT_A",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["racha"], 3)
        self.assertEqual(result["nivel"], "N1")
        self.assertEqual(
            result["fecha_fin"],
            "2024-06-30",
        )

    def test_latest_end_date_breaks_equal_length_tie(
        self,
    ) -> None:
        """
        If two eligible streaks have the same maximum length,
        the streak ending most recently must be selected.
        """

        rows = self.run_streaks(
            history=[
                ("CLIENT_A", "2024-01-31", 500000),   # N1
                ("CLIENT_A", "2024-02-29", 500000),   # N1

                ("CLIENT_A", "2024-03-31", 1500000),  # N2

                ("CLIENT_A", "2024-04-30", 3500000),  # N3
                ("CLIENT_A", "2024-05-31", 3500000),  # N3
            ],
            fecha_base="2024-05-31",
            n=2,
        )

        result = self.get_customer(
            rows,
            "CLIENT_A",
        )

        self.assertIsNotNone(result)

        # N1 streak = 2 months, ends February.
        # N3 streak = 2 months, ends May.
        # N3 must win because its fecha_fin is more recent.
        self.assertEqual(result["racha"], 2)
        self.assertEqual(result["nivel"], "N3")
        self.assertEqual(
            result["fecha_fin"],
            "2024-05-31",
        )

    def test_n_filters_short_streaks(
        self,
    ) -> None:
        """
        Customers without any streak >= n must not appear in
        the final result.
        """

        rows = self.run_streaks(
            history=[
                ("CLIENT_A", "2024-01-31", 500000),
                ("CLIENT_A", "2024-02-29", 500000),
                ("CLIENT_A", "2024-03-31", 1500000),
            ],
            fecha_base="2024-03-31",
            n=3,
        )

        result = self.get_customer(
            rows,
            "CLIENT_A",
        )

        self.assertIsNone(result)

    def test_fecha_base_after_source_horizon_does_not_create_future_n0(
        self,
    ) -> None:
        """
        A fecha_base later than the source horizon must not
        generate artificial N0 months beyond the last source
        monthly cut.
        """

        rows = self.run_streaks(
            history=[
                ("CLIENT_A", "2024-01-31", 500000),
                ("CLIENT_A", "2024-02-29", 500000),
            ],
            fecha_base="2024-12-31",
            n=3,
        )

        result = self.get_customer(
            rows,
            "CLIENT_A",
        )

        # Source ends in February.
        # March-December cannot be invented as N0.
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()