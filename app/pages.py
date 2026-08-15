from flask import Blueprint, current_app, render_template, send_from_directory

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def index():
    return render_template("index.html")


@pages_bp.get("/assets/<path:filename>")
def assets(filename):
    """Serve versioned assets (font, default banner) that ship with the repo."""
    return send_from_directory(current_app.config["ASSETS_DIR"], filename)
