# Google Drive Downloader

A Python tool to download and export files from Google Drive, with support for Google Docs, Sheets, Slides, PDFs, images, and more. Perfect for backing up files, importing data into other tools, or using Google Drive content as context in AI applications.

## Features

- **Interactive file selection** - Browse and select files from your Google Drive
- **Batch downloads** - Download all files or select specific ones
- **URL/ID-based downloads** - Download specific files using Drive URLs or file IDs
- **Smart format conversion** - Automatically exports Google Workspace files to portable formats:
  - Google Docs → Markdown (`.md`)
  - Google Sheets → CSV (`.csv`)
  - Google Slides → Plain text (`.txt`)
  - PDFs, images, and other files → Original format
- **Metadata tracking** - Saves modification dates and file IDs
- **Read-only access** - Uses read-only Google Drive scope for security
- **Works with any Google account** - Each user authenticates with their own credentials

## Prerequisites

- Python 3.8 or higher
- A Google account with access to Google Drive
- Google Cloud project with Drive API enabled (see setup instructions below)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/bassalat/google-drive-downloader.git
cd google-drive-downloader
```

### 2. Set Up Python Environment

This tool works with any Python environment manager. Choose your preferred method:

**Using venv (built-in):**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Using conda:**
```bash
conda create -n drive-downloader python=3.8
conda activate drive-downloader
pip install -r requirements.txt
```

**Using virtualenv:**
```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

**System-wide installation (not recommended):**
```bash
pip install -r requirements.txt
```

### 3. Google Cloud Setup

You'll need to create your own Google Cloud project and OAuth credentials. This is required for each user/account.

**Follow the detailed instructions in [GOOGLE_CLOUD_SETUP.md](GOOGLE_CLOUD_SETUP.md).**

**Quick summary:**
1. Create a Google Cloud project
2. Enable Google Drive, Docs, Sheets, and Slides APIs
3. Create OAuth 2.0 Desktop credentials
4. Download `credentials.json` to this directory

**Important:** The `credentials.json` file is specific to YOUR Google Cloud project. Each user must create their own.

## Usage

### Option 1: Interactive File Selection

Run the main script to browse and select files from your Google Drive:

```bash
python fetch_drive_files.py
```

**First time:**
- Opens browser for Google OAuth authorization
- Select your Google account and grant access
- Creates `token.pickle` for future authentication

**Subsequent runs:**
- Uses saved `token.pickle` (no browser needed)
- Lists all files in your Drive
- Enter file numbers (comma-separated) or `all` to download everything

**Example:**
```
Available files:
1. Project Plan.docx (Google Docs)
2. Budget 2024.xlsx (Google Sheets)
3. Presentation.pptx (Google Slides)
4. Report.pdf (PDF)

Enter file numbers to download (comma-separated), or 'all': 1,2,4
```

### Option 2: Download by URL or File ID

Download specific files directly using their Google Drive URL or file ID:

```bash
python download_by_url.py "https://docs.google.com/document/d/FILE_ID/edit"
```

Or use the file ID directly:

```bash
python download_by_url.py "FILE_ID"
```

**Multiple files:**
```bash
python download_by_url.py "URL1" "URL2" "FILE_ID3"
```

## File Type Support

| Google Drive Type | Export Format | Extension |
|-------------------|---------------|-----------|
| Google Docs | Markdown | `.md` |
| Google Sheets | CSV | `.csv` |
| Google Slides | Plain Text | `.txt` |
| PDF | Original | `.pdf` |
| Images (JPG, PNG, etc.) | Original | `.jpg`, `.png`, etc. |
| Other files | Original | Various |

## Output

All downloaded files are saved to the `./drive_files/` directory (created automatically).

Files are named using their original Drive filename with the appropriate extension.

## Security & Privacy

- **Read-only access:** Uses `drive.readonly` scope - cannot modify or delete your files
- **Local authentication:** OAuth tokens stored locally in `token.pickle`
- **No data sharing:** Your credentials and files stay on your machine
- **Gitignore protection:** `credentials.json`, `token.pickle`, and `drive_files/` are excluded from version control

**Never commit these files:**
- `credentials.json` - Your OAuth client credentials
- `token.pickle` - Your access tokens
- `drive_files/` - May contain sensitive downloaded content

## Troubleshooting

### "credentials.json not found"
- Make sure you've completed Google Cloud setup (see [GOOGLE_CLOUD_SETUP.md](GOOGLE_CLOUD_SETUP.md))
- Verify `credentials.json` is in the same directory as the scripts

### "Invalid credentials" or authentication errors
- Delete `token.pickle` to force re-authentication:
  ```bash
  rm token.pickle
  python fetch_drive_files.py
  ```

### "API not enabled" errors
- Ensure you've enabled all required APIs in Google Cloud Console:
  - Google Drive API
  - Google Docs API
  - Google Sheets API
  - Google Slides API

### Permission errors during OAuth
- Make sure you've added your email as a test user in the OAuth consent screen
- Select your Google account when prompted
- Click "Continue" when warned about unverified app (for personal projects)

## Advanced Usage

### Download from Specific Folder

Edit `fetch_drive_files.py` and modify the `main()` function:

```python
# Default: lists all files
files = list_files(service)

# Modified: list files from specific folder
files = list_files(service, folder_id='YOUR_FOLDER_ID')
```

### Change Export Formats

Edit the `EXPORT_FORMATS` dictionary in `fetch_drive_files.py`:

```python
EXPORT_FORMATS = {
    'application/vnd.google-apps.document': ('text/markdown', '.md'),
    'application/vnd.google-apps.spreadsheet': ('text/csv', '.csv'),
    'application/vnd.google-apps.presentation': ('text/plain', '.txt'),
}
```

Available export formats: https://developers.google.com/drive/api/guides/ref-export-formats

### Change Output Directory

Edit `OUTPUT_DIR` in `fetch_drive_files.py`:

```python
OUTPUT_DIR = Path('./your_custom_directory')
```

## Dependencies

- `google-api-python-client` - Google API client library
- `google-auth` - Authentication library
- `google-auth-httplib2` - HTTP transport for authentication
- `google-auth-oauthlib` - OAuth 2.0 flow implementation
- `requests` - HTTP library

See [requirements.txt](requirements.txt) for version details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review [GOOGLE_CLOUD_SETUP.md](GOOGLE_CLOUD_SETUP.md) for setup details
3. Open an issue on GitHub

## Acknowledgments

This tool uses the official Google Drive API and follows Google's best practices for OAuth 2.0 authentication.
