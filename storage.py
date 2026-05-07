import json
import os

STATE_DIR = os.path.join(os.path.dirname(__file__), "state")

def _ensure_dir():
    if not os.path.exists(STATE_DIR):
        os.makedirs(STATE_DIR)

def load_state(site_name: str) -> str | None:
    _ensure_dir()
    filepath = os.path.join(STATE_DIR, f"{site_name}_state.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("hash")
    return None

def save_state(site_name: str, content_hash: str):
    _ensure_dir()
    filepath = os.path.join(STATE_DIR, f"{site_name}_state.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"hash": content_hash}, f)

# Dla strony WSS2 potrzebujemy przechowywać cały fragment zamiast hasha
# (aby wyciągnąć dane do powiadomienia)
def load_wss2_raw() -> str | None:
    _ensure_dir()
    filepath = os.path.join(STATE_DIR, "wss2_raw.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("raw")
    return None

def save_wss2_raw(raw_content: str):
    _ensure_dir()
    filepath = os.path.join(STATE_DIR, "wss2_raw.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"raw": raw_content}, f)