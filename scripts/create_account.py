#!/usr/bin/env python3
"""Manage Event Banner Generator accounts.  """
"""
Usage:
    python scripts/create_account.py add <username> <password>
    python scripts/create_account.py remove <username>
    python scripts/create_account.py list
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash  # noqa: E402

from app import create_app  # noqa: E402
from app.storage import add_account, load_accounts, save_accounts  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Manage Event Banner Generator accounts.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Create a new account")
    add_p.add_argument("username")
    add_p.add_argument("password")

    rm_p = sub.add_parser("remove", help="Remove an account")
    rm_p.add_argument("username")

    sub.add_parser("list", help="List existing usernames")

    args = parser.parse_args()
    app = create_app()

    with app.app_context():
        accounts_file = app.config["ACCOUNTS_FILE"]

        if args.command == "add":
            password_hash = generate_password_hash(args.password)
            try:
                add_account(accounts_file, args.username, password_hash)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
            print(f"Account '{args.username}' created.")

        elif args.command == "remove":
            accounts = load_accounts(accounts_file)
            filtered = [a for a in accounts if a.get("username") != args.username]
            if len(filtered) == len(accounts):
                print(f"No account named '{args.username}' found.")
                sys.exit(1)
            save_accounts(accounts_file, filtered)
            print(f"Account '{args.username}' removed.")

        elif args.command == "list":
            accounts = load_accounts(accounts_file)
            if not accounts:
                print("No accounts yet.")
            for a in accounts:
                print(f"- {a.get('username')} (created {a.get('created_at', 'unknown')})")


if __name__ == "__main__":
    main()
