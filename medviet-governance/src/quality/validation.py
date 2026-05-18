import re
from pathlib import Path

import pandas as pd
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite


def build_patient_expectation_suite() -> ExpectationSuite:
    """
    Tạo expectation suite cho anonymized patient data.
    """
    context = gx.get_context()
    suite_name = "patient_data_suite"

    existing = context.list_expectation_suite_names()
    if suite_name in existing:
        context.delete_expectation_suite(expectation_suite_name=suite_name)

    suite = context.add_expectation_suite(expectation_suite_name=suite_name)

    df = pd.read_csv("data/raw/patients_raw.csv")
    validator = context.sources.pandas_default.read_dataframe(
        df,
        expectation_suite=suite,
    )

    validator.expect_column_values_to_not_be_null("patient_id")
    validator.expect_column_value_lengths_to_equal(column="cccd", value=12)
    validator.expect_column_values_to_be_between(
        column="ket_qua_xet_nghiem",
        min_value=0,
        max_value=50,
    )

    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    validator.expect_column_values_to_be_in_set(
        column="benh",
        value_set=valid_conditions,
    )

    validator.expect_column_values_to_match_regex(
        column="email",
        regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
    )

    validator.expect_column_values_to_be_unique(column="patient_id")

    validator.save_expectation_suite(discard_failed_expectations=False)
    return suite


def validate_anonymized_data(filepath: str) -> dict:
    """
    Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath)
    original_path = Path("data/raw/patients_raw.csv")
    original_df = pd.read_csv(original_path) if original_path.exists() else None

    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns),
        },
    }

    # Check 1: Không còn CCCD gốc dạng số thuần túy
    pure_cccd = df["cccd"].astype(str).str.match(r"^\d{12}$").sum()
    if pure_cccd > 0:
        results["success"] = False
        results["failed_checks"].append(
            f"Found {int(pure_cccd)} rows with raw 12-digit CCCD values"
        )

    # Check 2: Không có null values trong các cột quan trọng
    required_columns = ["patient_id", "cccd", "benh", "ket_qua_xet_nghiem"]
    for col in required_columns:
        null_count = int(df[col].isna().sum())
        if null_count > 0:
            results["success"] = False
            results["failed_checks"].append(
                f"Column '{col}' has {null_count} null values"
            )

    # Check 3: Số rows phải bằng original
    if original_df is not None and len(df) != len(original_df):
        results["success"] = False
        results["failed_checks"].append(
            f"Row count mismatch: anonymized={len(df)}, original={len(original_df)}"
        )

    # Supplemental checks aligned with expectation suite
    cccd_len_ok = df["cccd"].astype(str).str.len().eq(12).all()
    if not cccd_len_ok:
        results["success"] = False
        results["failed_checks"].append("Some CCCD values do not have length 12")

    range_ok = df["ket_qua_xet_nghiem"].between(0, 50, inclusive="both").all()
    if not range_ok:
        results["success"] = False
        results["failed_checks"].append(
            "ket_qua_xet_nghiem contains values outside [0, 50]"
        )

    valid_conditions = {"Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"}
    condition_ok = df["benh"].isin(valid_conditions).all()
    if not condition_ok:
        results["success"] = False
        results["failed_checks"].append("benh contains invalid disease labels")

    email_pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
    email_ok = df["email"].astype(str).map(lambda x: bool(email_pattern.match(x))).all()
    if not email_ok:
        results["success"] = False
        results["failed_checks"].append("email column contains invalid format")

    unique_ok = df["patient_id"].is_unique
    if not unique_ok:
        results["success"] = False
        results["failed_checks"].append("patient_id contains duplicates")

    return results
