"""Thread-safe helpers for the flat-JSON account and log stores.

This mirrors the JSON + lock pattern used elsewhere across Paper Engine
projects: simple, dependency-free persistence for a small, single-instance
Flask app. Writes go through a temp file + os.replace to avoid truncating
the file if the process dies mid-write.
"""
import json
import os
import threading
from datetime import datetime, timezone

_lock = threading.Lock()


def _read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def _write_json(path, data):
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, path)


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

def load_accounts(accounts_file):
    return _read_json(accounts_file, [])


def save_accounts(accounts_file, accounts):
    with _lock:
        _write_json(accounts_file, accounts)


def find_account(accounts_file, username):
    for account in load_accounts(accounts_file):
        if account.get("username") == username:
            return account
    return None


def add_account(accounts_file, username, password_hash):
    with _lock:
        accounts = _read_json(accounts_file, [])
        if any(a.get("username") == username for a in accounts):
            raise ValueError(f"Account '{username}' already exists.")
        accounts.append({
            "username": username,
            "password_hash": password_hash,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        _write_json(accounts_file, accounts)


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------

def load_logs(logs_file):
    return _read_json(logs_file, [])


def append_log(logs_file, entry):
    with _lock:
        logs = _read_json(logs_file, [])
        logs.append(entry)
        _write_json(logs_file, logs)
