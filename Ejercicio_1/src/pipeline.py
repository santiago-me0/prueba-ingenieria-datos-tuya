"""
Pipeline for creating a reliable customer phone dataset.
"""

import csv
from collections import defaultdict
from pathlib import Path

from Ejercicio_1.src.normalization import normalize_phone
from Ejercicio_1.src.validation import validate_phone


def process_dataset(input_path: str, output_path: str) -> None:
    """
    Process a customer phone dataset.

    The pipeline:
    1. Reads the original dataset.
    2. Normalizes phone numbers.
    3. Validates normalized phone numbers.
    4. Detects duplicated normalized phone numbers.
    5. Writes a processed dataset preserving the original value.
    """

    rows = _read_dataset(input_path)

    processed_rows = []

    for row in rows:
        customer_id = row["customer_id"]
        original_phone = row["phone"]

        normalized_phone = normalize_phone(original_phone)

        if normalized_phone is None:
            validation = {
                "phone_type": None,
                "status": "INVALID",
                "reason": (
                    "MISSING_VALUE"
                    if not original_phone or not original_phone.strip()
                    else "NORMALIZATION_FAILED"
                ),
            }
        else:
            validation = validate_phone(normalized_phone)

        processed_rows.append(
            {
                "customer_id": customer_id,
                "original_phone": original_phone,
                "normalized_phone": normalized_phone,
                "phone_type": validation["phone_type"],
                "status": validation["status"],
                "validation_reason": validation["reason"],
                "duplicate_group": None,
            }
        )

    _assign_duplicate_groups(processed_rows)

    _write_dataset(output_path, processed_rows)


def _read_dataset(input_path: str) -> list[dict]:
    """Read the input CSV dataset."""

    with open(input_path, mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        required_columns = {"customer_id", "phone"}

        if not required_columns.issubset(reader.fieldnames or set()):
            raise ValueError(
                "The input dataset must contain "
                "'customer_id' and 'phone' columns."
            )

        return list(reader)


def _assign_duplicate_groups(rows: list[dict]) -> None:
    """
    Assign a duplicate group to customers sharing
    the same normalized phone number.
    """

    phone_groups = defaultdict(list)

    for row in rows:
        normalized_phone = row["normalized_phone"]

        if normalized_phone is not None:
            phone_groups[normalized_phone].append(row)

    duplicate_counter = 1

    for normalized_phone, grouped_rows in phone_groups.items():

        if len(grouped_rows) > 1:
            group_id = f"DUP-{duplicate_counter:03d}"

            for row in grouped_rows:
                row["duplicate_group"] = group_id

            duplicate_counter += 1


def _write_dataset(output_path: str, rows: list[dict]) -> None:
    """Write the processed dataset to a CSV file."""

    output_file = Path(output_path)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "customer_id",
        "original_phone",
        "normalized_phone",
        "phone_type",
        "status",
        "validation_reason",
        "duplicate_group",
    ]

    with open(
        output_file,
        mode="w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":

    exercise_dir = Path(__file__).resolve().parents[1]

    input_file = exercise_dir / "data" / "clients.csv"
    output_file = exercise_dir / "data" / "processed_clients.csv"

    process_dataset(str(input_file), str(output_file))

    print(
        f"Dataset procesado correctamente: {output_file}"
    )