# fileManager.py
# Manages the files for the application (exe exclusive module)

import os
import sys
import shutil
from pathlib import Path

APP_NAME = "VaultMLN"


# ---------- internal helpers ----------

def _is_frozen():
    return getattr(sys, "frozen", False)


def _base_dir():
    """
    Directory where main.py / exe lives
    """
    # When bundled by PyInstaller, resources are extracted to a temporary
    # folder available at `sys._MEIPASS`. Prefer that when present.
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    if _is_frozen():
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent  # assumes Functions/ is sibling


# ---------- AppData paths ----------

def get_appdata_root() -> Path:
    """
    C:\\Users\\<user>\\AppData\\Roaming\\APP_NAME
    """
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME
    # Fallbacks for non-Windows or missing env
    if os.name == "nt":
        return Path.home() / "AppData" / "Roaming" / APP_NAME
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / APP_NAME
    return Path.home() / f".{APP_NAME}"


def get_data_dir() -> Path:
    """
    AppData/APP_NAME/Data
    """
    return get_appdata_root() / "Data"


def get_assets_dir() -> Path:
    """
    AppData/APP_NAME/assets
    """
    return get_appdata_root() / "assets"


# ---------- setup ----------

def ensure_appdata_structure():
    """
    Creates AppData folders if missing.
    Copies bundled assets on first run.
    """
    root = get_appdata_root()
    data_dir = get_data_dir()
    assets_dir = get_assets_dir()

    root.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    if not assets_dir.exists():
        _copy_initial_assets(assets_dir)


def _copy_initial_assets(target_assets_dir: Path):
    """
    Copies top-level 'assets/' folder into AppData
    """
    source_assets = _base_dir() / "assets"

    if not source_assets.exists():
        # no bundled assets, silently skip
        return

    try:
        shutil.copytree(source_assets, target_assets_dir)
    except Exception:
        # Fallback: try copying files individually
        target_assets_dir.mkdir(parents=True, exist_ok=True)
        for item in source_assets.iterdir():
            dest = target_assets_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)


# ---------- convenience ----------

def asset_path(relative_path: str) -> Path:
    """
    Returns full path to an asset inside AppData/assets
    """
    return get_assets_dir() / relative_path


def data_path(relative_path: str) -> Path:
    """
    Returns full path to a file inside AppData/Data
    """
    return get_data_dir() / relative_path
