# generatePass.py
# This script generates a symmetric encryption key and saves it to a file (Legacy file, not used in v1.0 +).
from cryptography.fernet import Fernet
from pathlib import Path


def generate_key(path: str = None):
    """Generate a Fernet key and save to Data/secret.key (or provided path)."""
    base = Path(__file__).resolve().parent.parent
    kp = base / "Data" / "secret.key" if path is None else Path(path)
    kp.parent.mkdir(parents=True, exist_ok=True)
    key = Fernet.generate_key()
    with open(kp, "wb") as f:
        f.write(key)
    return kp
