#!/usr/bin/env python3
"""
Download specific Google Drive files by URL or file ID

Usage:
    python download_by_url.py <url1> <url2> ...
    python download_by_url.py <file_id1> <file_id2> ...
    python download_by_url.py --format full-fidelity <url1> <url2> ...
"""

import os
import io
import re
import sys
import pickle
import argparse
from pathlib import Path
from typing import List

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

# Export format presets for different use cases
EXPORT_PRESETS = {
    'text-only': {
        'name': 'Text Only (optimized for AI/text processing)',
        'formats': {
            'application/vnd.google-apps.document': ('text/markdown', '.md'),
            'application/vnd.google-apps.spreadsheet': ('text/csv', '.csv'),
            'application/vnd.google-apps.presentation': ('text/plain', '.txt'),
        }
    },
    'full-fidelity': {
        'name': 'Full Fidelity (preserves images, formatting, multimedia)',
        'formats': {
            'application/vnd.google-apps.document': ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx'),
            'application/vnd.google-apps.spreadsheet': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx'),
            'application/vnd.google-apps.presentation': ('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx'),
        }
    },
    'pdf': {
        'name': 'PDF (universal format, preserves layout)',
        'formats': {
            'application/vnd.google-apps.document': ('application/pdf', '.pdf'),
            'application/vnd.google-apps.spreadsheet': ('application/pdf', '.pdf'),
            'application/vnd.google-apps.presentation': ('application/pdf', '.pdf'),
        }
    }
}

# Default export format (backward compatible)
EXPORT_FORMATS = EXPORT_PRESETS['text-only']['formats']


def set_export_preset(preset: str) -> None:
    """Set the export format preset globally."""
    global EXPORT_FORMATS
    if preset in EXPORT_PRESETS:
        EXPORT_FORMATS = EXPORT_PRESETS[preset]['formats']
    else:
        raise ValueError(f"Unknown preset: {preset}")


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


def extract_file_id(url_or_id: str) -> str:
    """Extract file ID from Google Drive URL or return as-is if already an ID."""
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


def get_file_info(service, file_id: str) -> dict:
    """Get file metadata from Google Drive."""
    try:
        file_info = service.files().get(
            fileId=file_id,
            fields='id, name, mimeType, modifiedTime'
        ).execute()
        return file_info
    except HttpError as error:
        print(f"❌ Error getting file info for {file_id}: {error}")
        return None


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

        # Write to file
        with open(output_path, 'wb') as f:
            f.write(file_data.getvalue())

        return True

    except HttpError as error:
        print(f"  ❌ Error downloading: {error}")
        return False


def download_file(service, file_id: str, output_dir: Path) -> tuple:
    """Download or export a file based on its type. Returns (success, file_info)."""
    # Get file info
    file_info = get_file_info(service, file_id)
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
        if export_google_file(service, file_id, mime_type, output_path):
            print(f"  ✅ Exported successfully")
            return True, file_info

    # Handle regular files (download)
    elif mime_type != 'application/vnd.google-apps.folder':
        if download_regular_file(service, file_id, output_path):
            print(f"  ✅ Downloaded successfully")
            return True, file_info

    return False, None


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Download specific Google Drive files by URL or file ID',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Export Format Presets:
  text-only       Docs→Markdown, Sheets→CSV, Slides→Text (default)
                  Best for: AI/LLM processing, text extraction
                  Note: Loses images and multimedia

  full-fidelity   Docs→DOCX, Sheets→XLSX, Slides→PPTX
                  Best for: Archival, editing, preserving all content
                  Preserves: Images, charts, formatting, multimedia

  pdf             All files→PDF
                  Best for: Viewing, sharing, printing
                  Preserves: Layout and formatting (no animations)

Examples:
  python download_by_url.py "https://docs.google.com/document/d/ABC123/edit"
  python download_by_url.py --format pdf "FILE_ID1" "FILE_ID2"
  python download_by_url.py -f full-fidelity "URL1" "URL2" "URL3"
        """
    )
    parser.add_argument(
        'files',
        nargs='+',
        metavar='URL_OR_ID',
        help='Google Drive URLs or file IDs to download'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['text-only', 'full-fidelity', 'pdf'],
        default='text-only',
        help='Export format preset (default: text-only)'
    )
    return parser.parse_args()


def main():
    """Main function to download specific Google Drive files."""
    # Parse arguments
    args = parse_arguments()

    # Set export format
    set_export_preset(args.format)

    # Extract file IDs from URLs or use as-is
    file_ids = [extract_file_id(url_or_id) for url_or_id in args.files]

    print("=" * 60)
    print("Google Drive File Downloader")
    print("=" * 60)
    print(f"📋 Export Format: {EXPORT_PRESETS[args.format]['name']}")
    print("=" * 60)
    print()

    # Authenticate
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # Download files
    print(f"📦 Downloading {len(file_ids)} file(s) to {OUTPUT_DIR}/\n")

    success_count = 0
    downloaded_files = []

    for file_id in file_ids:
        success, file_info = download_file(service, file_id, OUTPUT_DIR)
        if success:
            success_count += 1
            downloaded_files.append(file_info)
        print()

    # Create metadata file with modification dates
    if downloaded_files:
        metadata_path = OUTPUT_DIR / '_file_metadata.md'
        with open(metadata_path, 'w') as f:
            f.write("# Downloaded Files Metadata\n\n")
            f.write("Files are sorted by modification date (most recent first).\n\n")

            # Sort by modification date (most recent first)
            sorted_files = sorted(downloaded_files,
                                key=lambda x: x.get('modifiedTime', ''),
                                reverse=True)

            for file_info in sorted_files:
                f.write(f"## {file_info['name']}\n")
                f.write(f"- **Last Modified**: {file_info.get('modifiedTime', 'Unknown')}\n")
                f.write(f"- **File ID**: {file_info['id']}\n")
                f.write(f"- **Type**: {file_info['mimeType']}\n\n")

        print(f"📝 Metadata saved to: {metadata_path}")

    print("=" * 60)
    print(f"✅ Successfully downloaded {success_count}/{len(file_ids)} files")
    print(f"📁 Files saved to: {OUTPUT_DIR.absolute()}")
    print("=" * 60)


if __name__ == '__main__':
    main()
