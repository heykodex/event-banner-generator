import re
from functools import wraps

from flask import jsonify, session


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return jsonify({"ok": False, "error": "Not authenticated."}), 401
        return view(*args, **kwargs)
    return wrapped


def slugify(value):
    """Turn a username into a filesystem-safe slug for per-user files."""
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_") or "user"
