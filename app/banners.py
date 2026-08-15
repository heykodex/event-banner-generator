import base64
import io
import os
import re
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, send_file, session
from PIL import Image, ImageOps, UnidentifiedImageError

from .imaging import format_date_range, generate_banner_image
from .storage import append_log
from .utils import login_required, slugify

banners_bp = Blueprint("banners", __name__)


def _user_banner_path(username):
    """Path to a user's custom banner, if they've uploaded one."""
    path = os.path.join(current_app.config["BANNER_UPLOAD_DIR"], f"{slugify(username)}.png")
    return path if os.path.exists(path) else None


def _resolve_banner_path(username):
    """Custom banner if the user has published one, otherwise the shared default."""
    return _user_banner_path(username) or current_app.config["DEFAULT_BANNER_PATH"]


@banners_bp.get("/banner/status")
@login_required
def api_banner_status():
    has_custom = _user_banner_path(session["username"]) is not None
    return jsonify({"ok": True, "has_custom_banner": has_custom})


@banners_bp.post("/banner/upload")
@login_required
def api_banner_upload():
    file = request.files.get("banner")
    if file is None or file.filename == "":
        return jsonify({"ok": False, "error": "No file uploaded."}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in current_app.config["ALLOWED_BANNER_EXTENSIONS"]:
        return jsonify({"ok": False, "error": "Unsupported file type. Use PNG, JPG, or WEBP."}), 400

    try:
        probe = Image.open(file.stream)
        probe.verify()
        file.stream.seek(0)
        img = Image.open(file.stream).convert("RGB")
    except (UnidentifiedImageError, OSError):
        return jsonify({"ok": False, "error": "Could not read that image file."}), 400

    # Crop/scale to the shared banner canvas so text placement stays consistent
    target_size = current_app.config["BANNER_TARGET_SIZE"]
    fitted = ImageOps.fit(img, target_size, Image.LANCZOS)

    dest = os.path.join(current_app.config["BANNER_UPLOAD_DIR"], f"{slugify(session['username'])}.png")
    fitted.save(dest, "PNG")

    return jsonify({"ok": True})


@banners_bp.delete("/banner")
@login_required
def api_banner_reset():
    path = _user_banner_path(session["username"])
    if path:
        os.remove(path)
    return jsonify({"ok": True})


@banners_bp.post("/preview")
@login_required
def api_preview():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "")
    start_date = data.get("start_date", "")
    end_date = data.get("end_date", "")

    displayed_date = ""
    if start_date and end_date:
        try:
            displayed_date = format_date_range(start_date, end_date)
        except ValueError:
            displayed_date = ""

    banner_path = _resolve_banner_path(session["username"])
    img = generate_banner_image(banner_path, current_app.config["FONT_PATH"], title, displayed_date)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")

    return jsonify({
        "ok": True,
        "image": f"data:image/png;base64,{encoded}",
        "displayed_date": displayed_date,
    })


@banners_bp.post("/download")
@login_required
def api_download():
    data = request.get_json(silent=True) or {}
    title = (data.get("title", "") or "").strip()
    start_date = data.get("start_date", "")
    end_date = data.get("end_date", "")

    if not title or not start_date or not end_date:
        return jsonify({"ok": False, "error": "Title, start date, and end date are required."}), 400

    try:
        displayed_date = format_date_range(start_date, end_date)
    except ValueError:
        return jsonify({"ok": False, "error": "Invalid date format."}), 400

    banner_path = _resolve_banner_path(session["username"])
    img = generate_banner_image(banner_path, current_app.config["FONT_PATH"], title, displayed_date)

    timestamp = datetime.now().isoformat(timespec="seconds")
    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", title).strip("_") or "banner"
    filename = f"{safe_title}_{timestamp.replace(':', '-')}.png"
    filepath = os.path.join(current_app.config["OUTPUT_DIR"], filename)
    img.save(filepath, "PNG")

    append_log(current_app.config["LOGS_FILE"], {
        "username": session["username"],
        "title": title,
        "date": displayed_date,
        "created_at": timestamp,
    })

    return send_file(filepath, mimetype="image/png", as_attachment=True, download_name=filename)
