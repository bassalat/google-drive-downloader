#!/usr/bin/env python3
"""
Google Drive Client for Claude Code
Unified client for Drive operations with support for .drive-data/ structure
"""

import os
import io
import re
import pickle
from pathlib import Path
from typing import List, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# MIME type mappings for Google Workspace files
EXPORT_FORMATS = {
    'application/vnd.google-apps.document': ('text/markdown', '.md'),
    'application/vnd.google-apps.spreadsheet': ('text/csv', '.csv'),
    'application/vnd.google-apps.presentation': ('text/plain', '.txt'),
}


class DriveClient:
    """Google Drive client with support for .drive-data/ structure."""

    def __init__(self, data_dir: str = '.drive-data', output_dir: str = 'drive_files'):
        """Initialize Drive client.

        Args:
            data_dir: Directory containing credentials and token (default: .drive-data)
            output_dir: Directory for downloaded files (default: drive_files)
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.credentials_path = self.data_dir / 'credentials.json'
        self.token_path = self.data_dir / 'token.pickle'
        self.service = None

    def authenticate(self) -> Credentials:
        """Authenticate with Google Drive API using OAuth 2.0."""
        creds = None

        # Token file stores user's access and refresh tokens
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired credentials...")
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    print(f"\n❌ ERROR: {self.credentials_path} not found!")
                    print("Please run /drive-setup to configure this project.\n")
                    exit(1)

                print("\n🔐 Starting authentication flow...")
                print("A browser window will open for you to authorize access.\n")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
            print("✅ Authentication successful!\n")

        return creds

    def connect(self):
        """Connect to Google Drive API."""
        if not self.service:
            creds = self.authenticate()
            self.service = build('drive', 'v3', credentials=creds)
        return self.service

    def list_files(self, folder_id: Optional[str] = None, max_results: int = 100) -> List[Dict]:
        """List files in Google Drive.

        Args:
            folder_id: Optional folder ID to list files from
            max_results: Maximum number of files to return

        Returns:
            List of file metadata dictionaries
        """
        service = self.connect()
        try:
            query = "trashed = false"
            if folder_id:
                query += f" and '{folder_id}' in parents"

            results = service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, size, parents)"
            ).execute()

            return results.get('files', [])

        except HttpError as error:
            print(f"❌ An error occurred: {error}")
            return []

    def extract_file_id(self, url_or_id: str) -> str:
        """Extract file ID from Google Drive URL or return as-is if already an ID.

        Args:
            url_or_id: Google Drive URL or file ID

        Returns:
            File ID
        """
        # Pattern for Google Drive URLs
        patterns = [
            r'/d/([a-zA-Z0-9-_]+)',  # /d/FILE_ID
            r'id=([a-zA-Z0-9-_]+)',   # id=FILE_ID
        ]

        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)

        # If no pattern matches, assume it's already a file ID
        return url_or_id

    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """Get file metadata from Google Drive.

        Args:
            file_id: Google Drive file ID

        Returns:
            File metadata dictionary or None if error
        """
        service = self.connect()
        try:
            file_info = service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, modifiedTime, size'
            ).execute()
            return file_info
        except HttpError as error:
            print(f"❌ Error getting file info for {file_id}: {error}")
            return None

    def export_google_file(self, file_id: str, mime_type: str, output_path: Path) -> bool:
        """Export a Google Workspace file (Docs, Sheets, Slides).

        Args:
            file_id: Google Drive file ID
            mime_type: MIME type of the Google Workspace file
            output_path: Path to save the exported file

        Returns:
            True if successful, False otherwise
        """
        service = self.connect()
        try:
            export_mime, extension = EXPORT_FORMATS[mime_type]

            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
            file_data = io.BytesIO()
            downloader = MediaIoBaseDownload(file_data, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Write to file
            output_path = output_path.with_suffix(extension)
            with open(output_path, 'wb') as f:
                f.write(file_data.getvalue())

            return True

        except HttpError as error:
            print(f"  ❌ Error exporting: {error}")
            return False

    def download_regular_file(self, file_id: str, output_path: Path, show_progress: bool = True) -> bool:
        """Download a regular file (not a Google Workspace file).

        Args:
            file_id: Google Drive file ID
            output_path: Path to save the file
            show_progress: Whether to show download progress

        Returns:
            True if successful, False otherwise
        """
        service = self.connect()
        try:
            request = service.files().get_media(fileId=file_id)
            file_data = io.BytesIO()
            downloader = MediaIoBaseDownload(file_data, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status and show_progress:
                    print(f"  Download {int(status.progress() * 100)}%")

            # Write to file
            with open(output_path, 'wb') as f:
                f.write(file_data.getvalue())

            return True

        except HttpError as error:
            print(f"  ❌ Error downloading: {error}")
            return False

    def download_file(self, file_id: str, output_dir: Optional[Path] = None) -> tuple:
        """Download or export a file based on its type.

        Args:
            file_id: Google Drive file ID
            output_dir: Output directory (uses self.output_dir if not specified)

        Returns:
            Tuple of (success: bool, file_info: dict or None)
        """
        if output_dir is None:
            output_dir = self.output_dir

        # Get file info
        file_info = self.get_file_info(file_id)
        if not file_info:
            return False, None

        file_name = file_info['name']
        mime_type = file_info['mimeType']
        modified_time = file_info.get('modifiedTime', 'Unknown')

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / file_name

        print(f"📥 {file_name}")
        print(f"  📅 Last modified: {modified_time}")
        print(f"  🆔 File ID: {file_id}")

        # Handle Google Workspace files (export)
        if mime_type in EXPORT_FORMATS:
            if self.export_google_file(file_id, mime_type, output_path):
                print(f"  ✅ Exported successfully")
                return True, file_info

        # Handle regular files (download)
        elif mime_type != 'application/vnd.google-apps.folder':
            if self.download_regular_file(file_id, output_path):
                print(f"  ✅ Downloaded successfully")
                return True, file_info

        return False, None

    def download_files_by_urls(self, urls_or_ids: List[str]) -> Dict:
        """Download multiple files by URLs or IDs.

        Args:
            urls_or_ids: List of Google Drive URLs or file IDs

        Returns:
            Dictionary with download results
        """
        file_ids = [self.extract_file_id(url) for url in urls_or_ids]

        print(f"📦 Downloading {len(file_ids)} file(s) to {self.output_dir}/\n")

        success_count = 0
        downloaded_files = []

        for file_id in file_ids:
            success, file_info = self.download_file(file_id)
            if success:
                success_count += 1
                downloaded_files.append(file_info)
            print()

        return {
            'success_count': success_count,
            'total': len(file_ids),
            'files': downloaded_files
        }

    def interactive_fetch(self, max_results: int = 100):
        """Interactive file selection and download.

        Args:
            max_results: Maximum number of files to list
        """
        print("=" * 60)
        print("Google Drive File Fetcher for Claude Code")
        print("=" * 60)
        print()

        # List files
        print("📂 Fetching file list from Google Drive...\n")
        files = self.list_files(max_results=max_results)

        if not files:
            print("No files found in your Google Drive.")
            return

        print(f"Found {len(files)} files:\n")

        # Display files with numbers
        for idx, file in enumerate(files, 1):
            mime_type = file['mimeType']
            file_type = mime_type.split('.')[-1] if '.' in mime_type else mime_type
            print(f"{idx:3}. {file['name']:<40} ({file_type})")

        print("\n" + "=" * 60)
        print("Select files to download:")
        print("  - Enter numbers separated by commas (e.g., 1,2,5)")
        print("  - Enter 'all' to download all files")
        print("  - Enter 'q' to quit")
        print("=" * 60)

        selection = input("\nYour selection: ").strip().lower()

        if selection == 'q':
            print("Exiting...")
            return

        # Determine which files to download
        selected_files = []
        if selection == 'all':
            selected_files = files
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_files = [files[i] for i in indices if 0 <= i < len(files)]
            except (ValueError, IndexError):
                print("❌ Invalid selection. Please try again.")
                return

        if not selected_files:
            print("No files selected.")
            return

        # Download selected files
        print(f"\n📦 Downloading {len(selected_files)} file(s) to {self.output_dir}/\n")

        success_count = 0
        for file in selected_files:
            success, _ = self.download_file(file['id'])
            if success:
                success_count += 1

        print("\n" + "=" * 60)
        print(f"✅ Successfully downloaded {success_count}/{len(selected_files)} files")
        print(f"📁 Files saved to: {self.output_dir.absolute()}")
        print("=" * 60)
        print("\nYou can now use these files with Claude Code!")


def main():
    """Command-line interface for DriveClient."""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python drive_client.py fetch              # Interactive file selection")
        print("  python drive_client.py download <url1> <url2> ...  # Download by URL/ID")
        sys.exit(1)

    client = DriveClient()
    command = sys.argv[1]

    if command == 'fetch':
        client.interactive_fetch()
    elif command == 'download':
        if len(sys.argv) < 3:
            print("Please provide at least one URL or file ID")
            sys.exit(1)
        urls = sys.argv[2:]
        result = client.download_files_by_urls(urls)
        print("=" * 60)
        print(f"✅ Successfully downloaded {result['success_count']}/{result['total']} files")
        print(f"📁 Files saved to: {client.output_dir.absolute()}")
        print("=" * 60)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
