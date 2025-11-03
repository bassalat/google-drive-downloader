#!/usr/bin/env python3
"""
Google Drive Account Manager
Manages multiple Google Drive accounts with centralized credential storage.
"""

import os
import json
import shutil
from pathlib import Path


class DriveAccountManager:
    """Manages Google Drive accounts and their credentials."""

    def __init__(self, accounts_dir=None):
        """Initialize the account manager.

        Args:
            accounts_dir: Directory to store account credentials.
                         Defaults to ~/.drive-accounts/
        """
        if accounts_dir is None:
            accounts_dir = os.path.expanduser("~/.drive-accounts")
        self.accounts_dir = Path(accounts_dir)
        self.accounts_dir.mkdir(parents=True, exist_ok=True)

    def list_accounts(self):
        """List all available Drive accounts.

        Returns:
            list: Account names (directory names in accounts_dir)
        """
        if not self.accounts_dir.exists():
            return []

        accounts = []
        for item in self.accounts_dir.iterdir():
            if item.is_dir() and (item / "credentials.json").exists():
                accounts.append(item.name)
        return sorted(accounts)

    def get_account_path(self, account_name):
        """Get the path to an account's directory.

        Args:
            account_name: Name of the account

        Returns:
            Path: Path to the account directory
        """
        return self.accounts_dir / account_name

    def account_exists(self, account_name):
        """Check if an account exists.

        Args:
            account_name: Name of the account

        Returns:
            bool: True if account exists with valid credentials
        """
        account_path = self.get_account_path(account_name)
        return (account_path / "credentials.json").exists()

    def create_account(self, account_name, credentials_path):
        """Create a new account by copying credentials.

        Args:
            account_name: Name for the new account
            credentials_path: Path to credentials.json file

        Returns:
            bool: True if successful, False otherwise
        """
        account_path = self.get_account_path(account_name)
        account_path.mkdir(parents=True, exist_ok=True)

        try:
            dest = account_path / "credentials.json"
            shutil.copy2(credentials_path, dest)
            return True
        except Exception as e:
            print(f"Error creating account: {e}")
            return False

    def get_credentials_path(self, account_name):
        """Get the path to an account's credentials.json.

        Args:
            account_name: Name of the account

        Returns:
            Path: Path to credentials.json or None if not found
        """
        if not self.account_exists(account_name):
            return None
        return self.get_account_path(account_name) / "credentials.json"

    def setup_project(self, account_name, project_dir):
        """Set up a project directory to use a specific account.

        Args:
            account_name: Name of the account to use
            project_dir: Project directory to set up

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.account_exists(account_name):
            print(f"Account '{account_name}' does not exist")
            return False

        project_path = Path(project_dir)
        drive_data_dir = project_path / ".drive-data"
        drive_data_dir.mkdir(parents=True, exist_ok=True)

        # Copy credentials to project
        src_creds = self.get_credentials_path(account_name)
        dest_creds = drive_data_dir / "credentials.json"

        try:
            shutil.copy2(src_creds, dest_creds)

            # Create config file to track which account is being used
            config = {
                "account_name": account_name,
                "accounts_dir": str(self.accounts_dir)
            }
            with open(drive_data_dir / "config.json", "w") as f:
                json.dump(config, f, indent=2)

            return True
        except Exception as e:
            print(f"Error setting up project: {e}")
            return False

    def get_project_account(self, project_dir):
        """Get the account name used by a project.

        Args:
            project_dir: Project directory to check

        Returns:
            str: Account name or None if not configured
        """
        config_path = Path(project_dir) / ".drive-data" / "config.json"
        if not config_path.exists():
            return None

        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            return config.get("account_name")
        except Exception:
            return None


def main():
    """Command-line interface for account management."""
    import sys

    manager = DriveAccountManager()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python account_manager.py list")
        print("  python account_manager.py create <account_name> <credentials.json>")
        print("  python account_manager.py setup <account_name> <project_dir>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        accounts = manager.list_accounts()
        if accounts:
            print("Available accounts:")
            for account in accounts:
                print(f"  - {account}")
        else:
            print("No accounts found in ~/.drive-accounts/")

    elif command == "create":
        if len(sys.argv) != 4:
            print("Usage: python account_manager.py create <account_name> <credentials.json>")
            sys.exit(1)

        account_name = sys.argv[2]
        credentials_path = sys.argv[3]

        if manager.create_account(account_name, credentials_path):
            print(f"Account '{account_name}' created successfully")
        else:
            print(f"Failed to create account '{account_name}'")

    elif command == "setup":
        if len(sys.argv) != 4:
            print("Usage: python account_manager.py setup <account_name> <project_dir>")
            sys.exit(1)

        account_name = sys.argv[2]
        project_dir = sys.argv[3]

        if manager.setup_project(account_name, project_dir):
            print(f"Project set up with account '{account_name}'")
        else:
            print(f"Failed to set up project")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
