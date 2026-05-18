import json
from pathlib import Path

import pandas as pd

from src.encryption.vault import SimpleVault


def test_encryption_round_trip(tmp_path: Path):
    vault = SimpleVault(master_key_path=str(tmp_path / ".vault_key"))
    original = "Nguyen Van A - CCCD: 012345678901"

    encrypted = vault.encrypt_data(original)
    decrypted = vault.decrypt_data(encrypted)

    assert decrypted == original


def test_ciphertext_not_plaintext(tmp_path: Path):
    vault = SimpleVault(master_key_path=str(tmp_path / ".vault_key"))
    plaintext = "sensitive-value"

    encrypted = vault.encrypt_data(plaintext)

    assert encrypted["ciphertext"] != plaintext
    assert plaintext not in encrypted["ciphertext"]


def test_encrypt_column_works(tmp_path: Path):
    vault = SimpleVault(master_key_path=str(tmp_path / ".vault_key"))
    df = pd.DataFrame({"cccd": ["012345678901", "123456789012"], "benh": ["Khỏe mạnh", "Tim mạch"]})

    encrypted_df = vault.encrypt_column(df, "cccd")

    assert list(encrypted_df.columns) == ["cccd", "benh"]
    assert encrypted_df["benh"].tolist() == df["benh"].tolist()

    first_payload = json.loads(encrypted_df.loc[0, "cccd"])
    assert "encrypted_dek" in first_payload
    assert "ciphertext" in first_payload
    assert "algorithm" in first_payload

    recovered = vault.decrypt_data(first_payload)
    assert recovered == "012345678901"
