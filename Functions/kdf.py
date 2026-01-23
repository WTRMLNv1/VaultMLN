# Functions/kdf.py
# This module provides a key derivation function to derive a symmetric key from a master password and salt.
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode


def derive_key(master_password: str, salt: bytes) -> bytes:
    """Derive a URL-safe base64-encoded 32-byte key for Fernet.

    This uses PBKDF2-HMAC-SHA256 with a high iteration count.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend(),
    )
    return urlsafe_b64encode(kdf.derive(master_password.encode()))
