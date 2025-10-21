#!/usr/bin/env python3
"""
Google Drive File Fetcher

This script authenticates with Google Drive API and downloads/exports files
to a local directory for use with Claude Code.

Supports:
- Google Docs (exported as Markdown)
- Google Sheets (exported as CSV)
- Google Slides (exported as plain text)
- Regular files (PDF, images, etc.)
"""

import os
import io
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

# Output directory for downloaded files
OUTPUT_DIR = Path('./drive_files')

# MIME type mappings for Google Workspace files
EXPORT_FORMATS = {
    'application/vnd.google-apps.document': ('text/markdown', '.md'),
    'application/vnd.google-apps.spreadsheet': ('text/csv', '.csv'),
    'application/vnd.google-apps.presentation': ('text/plain', '.txt'),
}


def authenticate() -> Credentials:
    """Authenticate with Google Drive API using OAuth 2.0."""
    creds = None

    # Token file stores user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("\n❌ ERROR: credentials.json not found!")
                print("Please follow the setup instructions in GOOGLE_CLOUD_SETUP.md")
                print("to create and download your credentials.\n")
                exit(1)

            print("\n🔐 Starting authentication flow...")
            print("A browser window will open for you to authorize access.\n")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Authentication successful!\n")

    return creds


def list_files(service, folder_id: Optional[str] = None, max_results: int = 100) -> List[Dict]:
    """List files in Google Drive."""
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


def export_google_file(service, file_id: str, mime_type: str, output_path: Path) -> bool:
    """Export a Google Workspace file (Docs, Sheets, Slides)."""
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


def download_regular_file(service, file_id: str, output_path: Path) -> bool:
    """Download a regular file (not a Google Workspace file)."""
    try:
        request = service.files().get_media(fileId=file_id)
        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"  Download {int(status.progress() * 100)}%")

        # Write to file
        with open(output_path, 'wb') as f:
            f.write(file_data.getvalue())

        return True

    except HttpError as error:
        print(f"  ❌ Error downloading: {error}")
        return False


def download_file(service, file_info: Dict, output_dir: Path) -> bool:
    """Download or export a file based on its type."""
    file_id = file_info['id']
    file_name = file_info['name']
    mime_type = file_info['mimeType']

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / file_name

    print(f"📥 {file_name}")

    # Handle Google Workspace files (export)
    if mime_type in EXPORT_FORMATS:
        if export_google_file(service, file_id, mime_type, output_path):
            print(f"  ✅ Exported successfully")
            return True

    # Handle regular files (download)
    elif mime_type != 'application/vnd.google-apps.folder':
        if download_regular_file(service, file_id, output_path):
            print(f"  ✅ Downloaded successfully")
            return True

    return False


def main():
    """Main function to fetch Google Drive files."""
    print("=" * 60)
    print("Google Drive File Fetcher for Claude Code")
    print("=" * 60)
    print()

    # Authenticate
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # List files
    print("📂 Fetching file list from Google Drive...\n")
    files = list_files(service)

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
    print(f"\n📦 Downloading {len(selected_files)} file(s) to {OUTPUT_DIR}/\n")

    success_count = 0
    for file in selected_files:
        if download_file(service, file, OUTPUT_DIR):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"✅ Successfully downloaded {success_count}/{len(selected_files)} files")
    print(f"📁 Files saved to: {OUTPUT_DIR.absolute()}")
    print("=" * 60)
    print("\nYou can now use these files with Claude Code!")
    print("Example: Tell Claude to read files from the drive_files/ directory")


if __name__ == '__main__':
    main()
