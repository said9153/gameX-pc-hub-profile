from flask import Flask
import os, json

DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")

def default_payload():
    return {"products": [], "seq": 1}

def ensure_data_file():
    """
    Create or repair app/data.json.
    - If file missing -> create with default.
    - If file empty/invalid -> overwrite with default.
    """
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    needs_write = False
    if not os.path.exists(DATA_PATH):
        needs_write = True
    else:
        try:
            # If empty file or invalid JSON -> except block
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                txt = f.read().strip()
                if not txt:
                    needs_write = True
                else:
                    json.loads(txt)
        except Exception:
            needs_write = True

    if needs_write:
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(default_payload(), f, ensure_ascii=False, indent=2)

def create_app():
    ensure_data_file()
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "supersecretkey-change-this"

    from .route import main
    app.register_blueprint(main)
    return app
