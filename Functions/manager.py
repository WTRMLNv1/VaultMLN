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

    New stored JSON format is:
    {
      "site": [
          {"username": "<token>", "password": "<token>"},
          ...
      ]
    }
    """
    _ensure_key(master_password)
    data = _read_password_file()
    enc_user = encrypt.encrypt_message(user, master_password)
    enc_pass = encrypt.encrypt_message(password, master_password)
    entry = {"username": enc_user, "password": enc_pass}

    existing = data.get(site)
    if existing is None:
        data[site] = [entry]
    elif isinstance(existing, list):
        existing.append(entry)
        data[site] = existing
    elif isinstance(existing, dict):
        # legacy single-entry format -> convert to list
        data[site] = [existing, entry]
    else:
        data[site] = [entry]

    _write_password_file(data)


class Success(TypedDict):
    ok: bool
    user: list

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

    # Normalize to list for legacy and new formats
    entries = entry if isinstance(entry, list) else [entry]

    results: list[dict] = []
    try:
        for item in entries:
            # item may be legacy dict with keys 'user'/'password' or new with 'username'/'password'
            user_token = item.get("user") if "user" in item else item.get("username")
            pwd_token = item.get("password")
            results.append({
                "user": decrypt_message(user_token, master_password),
                "password": decrypt_message(pwd_token, master_password)
            })
        return {"ok": True, "user": results}
    except ValueError as e:
        logger.warning("Failed to decrypt entry for site %s: %s", site, e)
        return {"ok": False, "code": 403, "message": "Decryption failed"}

def list_sites(master_password: str) -> Dict[str, list]:
    """Return a dictionary of all stored sites with decrypted credentials.

    Each site maps to a list of entries: [{"user": str, "password": str}, ...]
    """
    _ensure_key(master_password)
    data = _read_password_file()
    result: dict = {}
    for site, creds in data.items():
        try:
            entries = creds if isinstance(creds, list) else [creds]
            decrypted: list[dict] = []
            for item in entries:
                try:
                    user_token = item.get("user") if "user" in item else item.get("username")
                    decrypted.append({
                        "user": decrypt_message(user_token, master_password),
                        "password": decrypt_message(item["password"], master_password)
                    })
                except ValueError:
                    decrypted.append({"user": None, "password": None})
            result[site] = decrypted
        except Exception:
            logger.debug("Could not process site %s", site)
            result[site] = []
    return result

def list_site_names() -> list[str]:
    """Return a list of all stored site names."""
    data = _read_password_file()
    return list(data.keys())

def delete_site(site: str, master_password: str, username: str | None = None) -> bool:
    """Delete entries.

    If `username` is None: delete entire site (legacy behavior).
    If `username` is provided: delete only the matching username entry (decrypted match).
    Returns True if something was deleted, False otherwise.
    """
    _ensure_key(master_password)
    data = _read_password_file()
    existing = data.get(site)
    if existing is None:
        return False

    # If no username provided, remove whole site
    if username is None:
        del data[site]
        _write_password_file(data)
        return True

    # Normalize to list
    entries = existing if isinstance(existing, list) else [existing]
    new_entries: list = []
    deleted = False
    for item in entries:
        # item may store encrypted under 'username' or legacy 'user'
        token = item.get("username") if "username" in item else item.get("user")
        try:
            decrypted = decrypt_message(token, master_password)
        except Exception:
            # If decryption fails, keep the entry to avoid accidental deletion
            new_entries.append(item)
            continue

        if decrypted == username:
            deleted = True
            # skip adding to new_entries to delete it
        else:
            new_entries.append(item)

    if deleted:
        if new_entries:
            data[site] = new_entries
        else:
            # no entries left for site
            del data[site]
        _write_password_file(data)
        return True

    return False

class SiteDisplayItem(TypedDict):
    label: str
    site: str
    username: str | None

class SiteDisplaySuccess(TypedDict):
    ok: bool
    items: list[SiteDisplayItem]

def get_site_display_names(master_password: str) -> SiteDisplaySuccess | Error:
    """
    Return site names for UI display.

    - If a site appears once, return just the site name.
    - If a site appears multiple times, append ' | {username}'.
    """
    _ensure_key(master_password)
    data = _read_password_file()

    if not data:
        return {"ok": False, "code": 404, "message": "No sites were found."}

    items: list[dict] = []

    for site, creds in data.items():
        entries = creds if isinstance(creds, list) else [creds]

        if len(entries) == 1:
            try:
                user = decrypt_message(
                    entries[0].get("username") or entries[0].get("user"),
                    master_password
                )
            except ValueError:
                user = None

            items.append({
                "label": site,
                "site": site,
                "username": None
            })
        else:
            for entry in entries:
                try:
                    user = decrypt_message(
                        entry.get("username") or entry.get("user"),
                        master_password
                    )
                except ValueError:
                    user = "<error>"

                items.append({
                    "label": f"{site} | {user}",
                    "site": site,
                    "username": user
                })

    return {"ok": True, "items": items}

