---
description: Fetch Google Drive files and make them available for analysis
---

# Google Drive Fetch Command

Fetch Google Drive files interactively and download them for use with Claude Code.

## Prerequisites Check

1. **Verify Setup Exists**
   - Check if `.drive-data/` directory exists in current working directory
   - Check if `.drive-data/credentials.json` exists
   - Check if `drive_client.py` exists in current directory
   - If any are missing, inform user to run `/drive-setup` first

2. **Check Account Configuration**
   - Read `.drive-data/config.json` to see which account is configured
   - Display account name to user for confirmation

## Steps to Execute

1. **Parse User Query** (if provided)
   - Look for file type requests (e.g., "PDFs", "documents", "spreadsheets")
   - Look for search terms or file names
   - Look for quantity requests (e.g., "latest 5", "all")
   - If no specific query, proceed with interactive mode

2. **Execute Interactive Fetch**
   - Run the drive_client.py script in fetch mode:
     ```bash
     python drive_client.py fetch
     ```
   - This will:
     - Authenticate (or use existing token)
     - List files from Google Drive
     - Display numbered list of files
     - Prompt user to select files to download
     - Download selected files to `drive_files/`

3. **Handle User Interaction**
   - The script runs interactively, so let the user interact with it directly
   - Script will show file list and accept input
   - User can enter:
     - Numbers separated by commas (e.g., "1,2,5")
     - "all" to download everything
     - "q" to quit

4. **Verify Downloads**
   - After script completes, check `drive_files/` directory
   - List downloaded files to user
   - Provide summary of what was downloaded

5. **Present Files to User**
   - Show the list of downloaded files
   - Explain that files are now available in `drive_files/`
   - Offer to read or analyze specific files if user wants

## Example Interactions

### User: "Fetch my Drive files"
```
🔍 Google Drive Fetch
==========================================
Using account: personal

Running interactive file browser...
[Script output showing files and prompts]

✅ Downloaded 3 files to drive_files/
  - Project_Proposal.md
  - Budget_2024.csv
  - Presentation_Slides.txt

Files are ready for analysis! Would you like me to read any of them?
```

### User: "Get the latest PDFs from Drive"
```
🔍 Google Drive Fetch
==========================================
Using account: work

Looking for PDF files in your Drive...
[Interactive selection of PDFs]

✅ Downloaded 2 PDFs to drive_files/
  - Annual_Report.pdf
  - Meeting_Notes.pdf

Would you like me to read these PDFs?
```

### User: "Fetch files from Drive and summarize them"
```
🔍 Google Drive Fetch
==========================================
Using account: personal

[Interactive fetch process]

✅ Downloaded 4 files to drive_files/
  - Document1.md
  - Document2.md
  - Spreadsheet.csv
  - Notes.txt

Now reading and summarizing the files...
[Proceed to read and summarize each file]
```

## Error Handling

- **No setup found**:
  - Message: "❌ Google Drive not set up in this directory. Run /drive-setup first."
  - Stop execution

- **Authentication fails**:
  - Show error from script
  - Suggest checking credentials or re-running /drive-setup

- **No files found**:
  - Message: "No files found in your Google Drive"
  - Ask if user wants to try different account

- **Download fails**:
  - Show which files failed to download
  - Explain possible reasons (permissions, file type, network)
  - List successfully downloaded files

## After Fetch Completion

1. **Offer Next Actions**
   - Ask if user wants to read specific files
   - Ask if user wants to analyze or summarize files
   - Ask if user wants to search within downloaded files

2. **Auto-Analysis** (if requested in original query)
   - If user said "fetch and summarize", automatically read files after download
   - If user said "fetch PDFs about X", search for relevant content after download

## Implementation Notes

- Use the Bash tool to run `python drive_client.py fetch`
- Let the script handle all Drive API interactions
- The script runs interactively, so don't try to programmatically provide input
- After completion, use Read tool to access downloaded files if needed
- Be helpful in offering to analyze or work with the downloaded files
- Remember that `.drive-data/` is hidden but `drive_files/` is visible
