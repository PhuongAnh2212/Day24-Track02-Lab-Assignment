from pathlib import Path

import pandas as pd

from src.quality.validation import build_patient_expectation_suite, validate_anonymized_data


def test_build_patient_expectation_suite_creates_suite():
    suite = build_patient_expectation_suite()
    assert suite is not None
    assert suite.expectation_suite_name == "patient_data_suite"


def test_validate_anonymized_data_success(tmp_path: Path):
    source = pd.read_csv("data/raw/patients_raw.csv")
    df = source.copy()

    # Make data look anonymized for checks.
    df["cccd"] = [f"{i:012d}"[::-1] for i in range(1, len(df) + 1)]
    df["cccd"] = [f"ID{v[2:]}" for v in df["cccd"]]  # keep length 12, avoid pure digits

    out_file = tmp_path / "patients_anonymized.csv"
    df.to_csv(out_file, index=False)

    result = validate_anonymized_data(str(out_file))

    assert result["success"] is True
    assert result["failed_checks"] == []
    assert result["stats"]["total_rows"] == len(df)


def test_validate_anonymized_data_detects_raw_cccd(tmp_path: Path):
    source = pd.read_csv("data/raw/patients_raw.csv")

    out_file = tmp_path / "patients_anonymized_bad.csv"
    source.to_csv(out_file, index=False)

    result = validate_anonymized_data(str(out_file))

    assert result["success"] is False
    assert any("CCCD" in msg for msg in result["failed_checks"])
