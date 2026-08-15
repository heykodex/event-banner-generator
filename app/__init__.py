import os

from dotenv import load_dotenv
from flask import Flask

from .config import DevelopmentConfig, ProductionConfig

load_dotenv()


def create_app():
    """Application factory for the Event Banner Generator."""
    app = Flask(__name__, instance_relative_config=True)

    env = os.environ.get("FLASK_ENV", "production")
    app.config.from_object(DevelopmentConfig if env == "development" else ProductionConfig)

    # -- instance-relative, non-versioned data (accounts, logs, uploads) --
    os.makedirs(app.instance_path, exist_ok=True)

    banner_upload_dir = os.path.join(app.instance_path, "uploads", "banners")
    output_dir = os.path.join(app.instance_path, "output")
    os.makedirs(banner_upload_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    app.config["ACCOUNTS_FILE"] = os.path.join(app.instance_path, "accounts.json")
    app.config["LOGS_FILE"] = os.path.join(app.instance_path, "logs.json")
    app.config["BANNER_UPLOAD_DIR"] = banner_upload_dir
    app.config["OUTPUT_DIR"] = output_dir

    # -- versioned static assets shipped with the repo --
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, "assets")
    app.config["ASSETS_DIR"] = assets_dir
    app.config["DEFAULT_BANNER_PATH"] = os.path.join(assets_dir, "default_banner.webp")
    app.config["FONT_PATH"] = os.path.join(assets_dir, "DelaGothicOne-Regular.ttf")

    from .auth import auth_bp
    from .banners import banners_bp
    from .pages import pages_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(banners_bp, url_prefix="/api")

    return app
