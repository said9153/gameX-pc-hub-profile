from flask import Flask
from .models import create_db_and_tables, get_engine
import os

def create_app():
    """
    Flask application factory.
    - Uses DATABASE_URL from environment variable if provided.
    - Automatically creates tables on startup.
    """
    app = Flask(__name__, template_folder="templates")
    app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey-change-this")

    # Initialize SQLAlchemy tables
    engine = get_engine()
    create_db_and_tables(engine)

    # Register main blueprint
    from .route import main
    app.register_blueprint(main)

    # Optional: Root sanity route
    @app.route("/ping")
    def ping():
        return {"status": "ok", "message": "GameX API running"}

    return app
