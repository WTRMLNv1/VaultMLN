# Functions/encrypt.py
# This module provides functions to encrypt and decrypt messages using a symmetric key.
from cryptography.fernet import Fernet, InvalidToken
from pathlib import Path
from typing import Optional

from Functions.kdf import derive_key
from Functions.salt import load_or_create_salt

BASE_DIR = Path(__file__).resolve().parent.parent


def _key_path():
    return BASE_DIR / "Data" / "secret.key"


def load_key():
    """Load the previously generated key from Data/secret.key.

    Raises FileNotFoundError if the key is missing.
    """
    kp = _key_path()
    if not kp.exists():
        raise FileNotFoundError(f"Legacy key not found at {kp}")
    with open(kp, "rb") as f:
        return f.read()


def ensure_key():
    """Generate and save a Fernet key if it doesn't already exist.

    This remains for backward compatibility with the file-based key.
    """
    kp = _key_path()
    if not kp.exists():
        kp.parent.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        with open(kp, "wb") as f:
            f.write(key)
    return load_key()


def get_fernet(master_password: str) -> Fernet:
    """Return a Fernet instance derived from `master_password` and salt.

    `master_password` is required. Use `load_key()` only for migration.
    """
    if not master_password:
        raise ValueError("master_password is required")
    salt = load_or_create_salt()
    key = derive_key(master_password, salt)
    return Fernet(key)


def encrypt_message(message: str, master_password: str) -> str:
    """Encrypt `message` using a key derived from `master_password`."""
    if not master_password:
        raise ValueError("master_password is required for encryption")
    f = get_fernet(master_password)
    token = f.encrypt(message.encode())
    return token.decode("utf-8")


def decrypt_message(token: str, master_password: str) -> str:
    """Decrypt `token` using a key derived from `master_password`."""
    if not master_password:
        raise ValueError("master_password is required for decryption")
    f = get_fernet(master_password)
    try:
        plaintext = f.decrypt(token.encode())
    except InvalidToken as exc:
        raise ValueError("Decryption failed: invalid token or wrong master password") from exc
    return plaintext.decode("utf-8")
