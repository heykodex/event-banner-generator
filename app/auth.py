from flask import Blueprint, current_app, jsonify, request, session
from werkzeug.security import check_password_hash

from .storage import find_account, load_accounts

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/usernames")
def api_usernames():
    accounts = load_accounts(current_app.config["ACCOUNTS_FILE"])
    usernames = sorted(a.get("username", "") for a in accounts if a.get("username"))
    return jsonify(usernames)


@auth_bp.post("/login")
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"ok": False, "error": "Username and password required."}), 400

    account = find_account(current_app.config["ACCOUNTS_FILE"], username)
    if account is None or not check_password_hash(account.get("password_hash", ""), password):
        return jsonify({"ok": False, "error": "Invalid username or password."}), 401

    session.clear()
    session["username"] = username
    return jsonify({"ok": True, "username": username})


@auth_bp.post("/logout")
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@auth_bp.get("/me")
def api_me():
    if "username" in session:
        return jsonify({"logged_in": True, "username": session["username"]})
    return jsonify({"logged_in": False})
