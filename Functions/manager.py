# manager.py
# A simple password manager that stores encrypted credentials in a JSON file.
from pathlib import Path
import json
from typing import Dict
import logging
from typing import TypedDict
from Functions import encrypt
from Functions.salt import load_or_create_salt

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
PASSWORD_FILE = DATA_DIR / "password.json"


def _ensure_key(master_password: str | None = None):
    """Ensure required crypto material exists.

    If `master_password` is provided, ensure salt exists. Otherwise ensure
    the legacy file-based key exists (for backward compatibility).
    """
    if master_password:
        try:
            load_or_create_salt()
        except Exception as e:
            logger.exception("Failed to create/load salt: %s", e)
            raise
        return
    try:
        encrypt.load_key()
    except Exception:
        encrypt.ensure_key()


def encrypt_message(message: str, master_password: str) -> str:
    _ensure_key(master_password)
    return encrypt.encrypt_message(message, master_password)


def decrypt_message(token: str, master_password: str) -> str:
    _ensure_key(master_password)
    return encrypt.decrypt_message(token, master_password)


def _read_password_file() -> Dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PASSWORD_FILE.exists():
        PASSWORD_FILE.write_text("{}")
        return {}
    try:
        with open(PASSWORD_FILE, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except json.JSONDecodeError:
        # backup corrupted file
        backup = PASSWORD_FILE.with_name("password_backup.json")
        PASSWORD_FILE.replace(backup)
        PASSWORD_FILE.write_text("{}")
        return {}


def _write_password_file(data: Dict):
    with open(PASSWORD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def store_json(site: str, user: str, password: str, master_password: str) -> None:
    """Store encrypted user/password under site name.

    The stored JSON format is:
    {
      "site": {"user": "<token>", "password": "<token>"}
    }
    """
    _ensure_key(master_password)
    data = _read_password_file()
    enc_user = encrypt.encrypt_message(user, master_password)
    enc_pass = encrypt.encrypt_message(password, master_password)
    data[site] = {"user": enc_user, "password": enc_pass}
    _write_password_file(data)


class Success(TypedDict):
    ok: bool
    user: str
    password: str

class Error(TypedDict):
    ok: bool
    code: int
    message: str

def get_data(site: str, master_password: str) -> Success | Error:
    """Return decrypted credentials for site, or Error dictionary if any errors."""
    _ensure_key(master_password)
    data = _read_password_file()
    entry = data.get(site)
    if not entry:
        return {"ok": False, "code": 404, "message": "Site not found"}
    try:
        return {"ok": True, "user": decrypt_message(entry["user"], master_password), "password": decrypt_message(entry["password"], master_password)}
    except ValueError as e:
        logger.warning("Failed to decrypt entry for site %s: %s", site, e)
        return {"ok": False, "code": 403, "message": "Decryption failed"}

def list_sites(master_password: str) -> Dict[str, Dict[str, str]]:
    """Return a dictionary of all stored sites with decrypted credentials."""
    _ensure_key(master_password)
    data = _read_password_file()
    result = {}
    for site, creds in data.items():
        try:
            result[site] = {
                "user": decrypt_message(creds["user"], master_password),
                "password": decrypt_message(creds["password"], master_password)
            }
        except ValueError:
            logger.debug("Could not decrypt site %s with provided master password", site)
            result[site] = {"user": None, "password": None}
    return result

def delete_site(site: str, master_password: str) -> bool:
    """Delete the entry for the given site. Returns True if deleted, False if not found."""
    _ensure_key(master_password)
    data = _read_password_file()
    if site in data:
        del data[site]
        _write_password_file(data)
        return True
    return False

# example adding a new password entry
