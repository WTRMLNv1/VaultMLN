from pathlib import Path
import os

# Place salt in the AppData Data directory
from Functions import fileManager
SALT_PATH = fileManager.data_path("salt.bin")


def load_or_create_salt() -> bytes:
    """Return salt bytes, creating a random 16-byte salt if missing.

    Salt is stored in the top-level `Data` folder to avoid duplicating
    data folders under `Functions`.
    """
    if not SALT_PATH.exists():
        SALT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SALT_PATH.write_bytes(os.urandom(16))
    return SALT_PATH.read_bytes()
