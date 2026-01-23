# themeManager.py
# Gets the themes from config.py
import json
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")


DATA_FILE = f"{BASE_DIR}/Data/themes.json"

def ensure_config_file():
    try:
        with open(DATA_FILE, "r") as file:
            json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        default_config = {
            "theme": {
                "accent": "#8B5CF6",
            }
        }
        with open(DATA_FILE, "w") as file:
            json.dump(default_config, file, indent=4)

def load_config():
    ensure_config_file()
    with open(DATA_FILE, "r") as file:
        return json.load(file)

def save_config(config: dict):
    with open(DATA_FILE, "w") as file:
        json.dump(config, file, indent=4)

def get_theme():
    config = load_config()
    theme = config.get("theme", {"accent": "#8B5CF6"})
    # Return the accent color string for compatibility with callers
    if isinstance(theme, dict):
        return theme.get("accent", "#8B5CF6")
    # Fallback if stored as a string
    return theme

def set_theme(accent_color: str):
    config = load_config()
    config["theme"] = {
        "accent": accent_color
    }
    save_config(config)
