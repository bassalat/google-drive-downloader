---
description: Set up Google Drive downloader in current project with account selection
---

# Google Drive Setup Command

Set up Google Drive downloader in the current project directory with account selection from centralized credentials.

## Steps to Execute

1. **Check for Existing Setup**
   - Look for `.drive-data/` directory in current working directory
   - If it exists and has `credentials.json`, inform the user that setup already exists
   - Ask if they want to reconfigure (which will use a different account)

2. **List Available Accounts**
   - Check `~/.drive-accounts/` directory for existing accounts
   - List all subdirectories that contain `credentials.json`
   - Show account names to the user

3. **Account Selection**
   - If accounts exist, ask user to:
     - Select an existing account by name
     - Or add a new account
   - If no accounts exist, guide user to add first account

4. **Adding New Account** (if selected)
   - Ask user for an account name (e.g., "personal", "work", "client-name")
   - Ask for the path to their `credentials.json` file
   - Verify the credentials file exists and is valid JSON
   - Create `~/.drive-accounts/<account_name>/` directory
   - Copy `credentials.json` to `~/.drive-accounts/<account_name>/credentials.json`
   - Confirm account created successfully

5. **Copy Drive Client to Project**
   - Copy `/Users/bassalat/Documents/tools/google-drive-downloader/drive_client.py` to current directory
   - Confirm file copied successfully

6. **Set Up Project with Selected Account**
   - Use the `account_manager.py` to link the account to current project
   - This will:
     - Create `.drive-data/` directory
     - Copy `credentials.json` from account to `.drive-data/`
     - Create `config.json` in `.drive-data/` with account info
   - Create `drive_files/` directory for downloads

7. **Guide OAuth Authentication**
   - Inform user that first use will require OAuth authentication
   - Explain: "When you run /drive-fetch or /drive-download for the first time, a browser will open for you to authorize access"
   - Explain: "After authorization, a token will be saved in .drive-data/token.pickle for future use"

8. **Verify Setup**
   - Confirm all files are in place:
     - `drive_client.py` in current directory
     - `.drive-data/credentials.json` exists
     - `.drive-data/config.json` exists
     - `drive_files/` directory exists
   - Display success message with next steps

## Example Output Format

```
🔧 Google Drive Setup
==========================================

✅ Found existing accounts in ~/.drive-accounts/:
  1. personal
  2. work

Select an account or add new:
  - Enter number to select existing account
  - Enter 'new' to add a new account
  - Enter 'q' to quit

[User selects option]

✅ Using account: personal
✅ Copied drive_client.py to current directory
✅ Created .drive-data/ with credentials
✅ Created drive_files/ for downloads

🎉 Setup Complete!

Next steps:
  - Run /drive-fetch to interactively browse and download files
  - Run /drive-download <url> to download specific files by URL

First use will open a browser for OAuth authorization.
```

## Error Handling

- If `~/.drive-accounts/` doesn't exist, create it
- If credentials file path is invalid, ask again
- If credentials file is not valid JSON, show error and ask for valid file
- If account name already exists, ask if user wants to overwrite
- If copying files fails, show clear error message

## Implementation Notes

- Use Python's `account_manager.py` from `/Users/bassalat/Documents/tools/google-drive-downloader/` to manage accounts
- Execute setup steps sequentially, showing progress to user
- Use the Bash tool to run Python scripts when needed
- Check for successful completion at each step before proceeding
- All interaction should be clear and user-friendly
