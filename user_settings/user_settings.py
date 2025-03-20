import json
import os

SETTINGS_FILE = "user_settings.json"
THEMES_FILE = "themes.json"

def save_user_settings(settings):
    """Save user settings to a JSON file."""
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)

def load_user_settings():
    """Load user settings from a JSON file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    return {}

def load_themes():
    """Load available themes from themes.json."""
    if os.path.exists(THEMES_FILE):
        with open(THEMES_FILE, "r") as file:
            return json.load(file)
    return {"default_theme": "cyborg", "themes": ["cyborg", "superhero", "solar", "darkly", "vapor"]}
