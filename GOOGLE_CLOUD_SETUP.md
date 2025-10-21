# Google Cloud Setup Instructions

Follow these steps to set up Google Drive API access:

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "Drive Access for Claude")
5. Click "Create"

## Step 2: Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for and enable the following APIs:
   - **Google Drive API**
   - **Google Docs API**
   - **Google Sheets API**
   - **Google Slides API**
3. Click "Enable" for each API

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: Select "External"
   - App name: Enter a name (e.g., "Drive Access")
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - On Scopes page, click "Save and Continue"
   - On Test users page, add your email address
   - Click "Save and Continue"
4. Back on Create OAuth client ID:
   - Application type: Select "Desktop app"
   - Name: Enter a name (e.g., "Drive Desktop Client")
   - Click "Create"
5. Download the credentials:
   - Click "Download JSON" on the credentials you just created
   - Save the file as `credentials.json` in the project directory (where you cloned this repository)

## Step 4: Security Note

⚠️ **IMPORTANT**: The `credentials.json` file contains sensitive information.
- Do NOT commit it to version control
- Keep it secure
- It's already included in `.gitignore` to prevent accidental commits

## Next Steps

After completing these steps:
1. Ensure `credentials.json` is in the project directory
2. Run `pip install -r requirements.txt` to install dependencies (using your preferred Python environment)
3. Run the Python script to authenticate and download files
