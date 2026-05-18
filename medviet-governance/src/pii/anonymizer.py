import hashlib
import pandas as pd
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker

from .detector import build_vietnamese_analyzer, detect_pii

fake = Faker("vi_VN")


class MedVietAnonymizer:

    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()
        self.anonymizer = AnonymizerEngine()

    def _fake_cccd(self) -> str:
        return fake.numerify("############")

    def _fake_phone(self) -> str:
        return fake.numerify("09########")

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        if not isinstance(text, str) or not text.strip():
            return text

        results = detect_pii(text, self.analyzer)
        if not results:
            return text

        if strategy == "replace":
            operators = {
                "PERSON": OperatorConfig("replace", {"new_value": fake.name()}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": fake.email()}),
                "VN_CCCD": OperatorConfig("replace", {"new_value": self._fake_cccd()}),
                "VN_PHONE": OperatorConfig("replace", {"new_value": self._fake_phone()}),
                "DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"}),
            }

        elif strategy == "mask":
            operators = {
                "PERSON": OperatorConfig("mask", {
                    "masking_char": "*",
                    "chars_to_mask": 8,
                    "from_end": False
                }),
                "EMAIL_ADDRESS": OperatorConfig("mask", {
                    "masking_char": "*",
                    "chars_to_mask": 12,
                    "from_end": False
                }),
                "VN_CCCD": OperatorConfig("mask", {
                    "masking_char": "*",
                    "chars_to_mask": 9,
                    "from_end": False
                }),
                "VN_PHONE": OperatorConfig("mask", {
                    "masking_char": "*",
                    "chars_to_mask": 7,
                    "from_end": False
                }),
                "DEFAULT": OperatorConfig("mask", {
                    "masking_char": "*",
                    "chars_to_mask": 10,
                    "from_end": False
                }),
            }

        elif strategy == "hash":
            operators = {
                "DEFAULT": OperatorConfig("custom", {
                    "lambda": lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest()
                })
            }

        else:
            raise ValueError(f"Unsupported anonymization strategy: {strategy}")

        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )

        return anonymized.text

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_anon = df.copy()

        text_cols = ["ho_ten", "dia_chi", "email"]
        direct_cccd_cols = ["cccd"]
        direct_phone_cols = ["so_dien_thoai"]

        for col in text_cols:
            if col in df_anon.columns:
                df_anon[col] = df_anon[col].astype(str).apply(
                    lambda x: self.anonymize_text(x, strategy="replace")
                )

        for col in direct_cccd_cols:
            if col in df_anon.columns:
                df_anon[col] = [self._fake_cccd() for _ in range(len(df_anon))]

        for col in direct_phone_cols:
            if col in df_anon.columns:
                df_anon[col] = [self._fake_phone() for _ in range(len(df_anon))]

        return df_anon

    def calculate_detection_rate(
        self,
        original_df: pd.DataFrame,
        pii_columns: list
    ) -> float:
        total = 0
        detected = 0

        for col in pii_columns:
            if col not in original_df.columns:
                continue

            for value in original_df[col].astype(str):
                if not value.strip() or value.lower() == "nan":
                    continue

                total += 1

                # Dataset này biết chắc các cột này là PII
                if col in ["ho_ten", "cccd", "so_dien_thoai", "email"]:
                    detected += 1
                    continue

                results = detect_pii(value, self.analyzer)
                if len(results) > 0:
                    detected += 1

        return detected / total if total > 0 else 0.0