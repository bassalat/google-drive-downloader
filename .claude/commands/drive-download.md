---
description: Download specific files by URL or ID
---

# Google Drive Download Command

Download specific Google Drive files by URL or file ID. This is useful when you know exactly which files to download without browsing.

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

1. **Extract Drive URLs or IDs from User Message**
   - Look for Google Drive URLs in the user's message
   - Common URL patterns:
     - `https://drive.google.com/file/d/FILE_ID/view`
     - `https://drive.google.com/open?id=FILE_ID`
     - `https://docs.google.com/document/d/FILE_ID/edit`
     - `https://docs.google.com/spreadsheets/d/FILE_ID/edit`
   - Also accept raw file IDs (alphanumeric strings)
   - Extract all URLs/IDs found

2. **Validate Input**
   - Ensure at least one URL or ID was provided
   - If none found, ask user to provide Drive URLs or file IDs

3. **Download Files**
   - Run drive_client.py with download command:
     ```bash
     python drive_client.py download <url1> <url2> <url3>
     ```
   - The script will:
     - Authenticate (or use existing token)
     - Extract file IDs from URLs
     - Get file metadata
     - Download each file to `drive_files/`
     - Show progress for each file

4. **Report Results**
   - List successfully downloaded files
   - Show any failed downloads with reasons
   - Display location where files were saved

5. **Offer Next Actions**
   - Ask if user wants to read or analyze the downloaded files
   - Offer to perform any operations they mentioned in original request

## Example Interactions

### User: "Download this file https://drive.google.com/file/d/1ABC123XYZ/view"
```
📥 Google Drive Download
==========================================
Using account: personal

Downloading 1 file...

📥 Project_Document.md
  📅 Last modified: 2024-01-15T10:30:00.000Z
  🆔 File ID: 1ABC123XYZ
  ✅ Downloaded successfully

✅ Successfully downloaded 1/1 files
📁 Files saved to: /path/to/drive_files/

Would you like me to read Project_Document.md?
```

### User: "Download these docs: [URL1] [URL2] [URL3] and summarize them"
```
📥 Google Drive Download
==========================================
Using account: work

Downloading 3 files...

📥 Q1_Report.md
  ✅ Downloaded successfully

📥 Q2_Report.md
  ✅ Downloaded successfully

📥 Annual_Summary.csv
  ✅ Downloaded successfully

✅ Successfully downloaded 3/3 files
📁 Files saved to: /path/to/drive_files/

Now reading and summarizing the documents...
[Proceed to read and summarize each file]
```

### User: "Get file ID 1XYZ789ABC and analyze it"
```
📥 Google Drive Download
==========================================
Using account: personal

Downloading file by ID...

📥 Analysis_Report.md
  📅 Last modified: 2024-01-10T15:45:00.000Z
  🆔 File ID: 1XYZ789ABC
  ✅ Downloaded successfully

✅ Successfully downloaded 1/1 files

Now analyzing Analysis_Report.md...
[Proceed with analysis]
```

## Error Handling

- **No setup found**:
  - Message: "❌ Google Drive not set up in this directory. Run /drive-setup first."
  - Stop execution

- **No URLs/IDs provided**:
  - Message: "Please provide Google Drive URLs or file IDs to download."
  - Show example: "/drive-download https://drive.google.com/file/d/FILE_ID/view"

- **Invalid URL/ID**:
  - Show which URL/ID is invalid
  - Continue with other valid URLs if multiple provided

- **Authentication fails**:
  - Show error from script
  - Suggest checking credentials or re-running /drive-setup

- **File not found or no access**:
  - Message: "❌ Cannot access file [ID]. Check that you have permission to view it."
  - Continue with other files if multiple provided

- **Download fails**:
  - Show clear error for each failed file
  - List successfully downloaded files
  - Suggest possible fixes (check permissions, network, etc.)

## URL Pattern Extraction

Support these Google Drive URL patterns:
- `https://drive.google.com/file/d/{FILE_ID}/view`
- `https://drive.google.com/file/d/{FILE_ID}/edit`
- `https://drive.google.com/open?id={FILE_ID}`
- `https://docs.google.com/document/d/{FILE_ID}/edit`
- `https://docs.google.com/spreadsheets/d/{FILE_ID}/edit`
- `https://docs.google.com/presentation/d/{FILE_ID}/edit`
- Raw file IDs (alphanumeric strings like "1ABC123XYZ456")

## After Download Completion

1. **Auto-Analysis** (if requested)
   - If user said "download and read", automatically read files
   - If user said "download and summarize", summarize the content
   - If user said "download and analyze X", perform specific analysis

2. **Offer Assistance**
   - Ask what user wants to do with downloaded files
   - Offer to read, search, summarize, or analyze content
   - Be proactive if user's intent is clear from their request

## Implementation Notes

- Use Bash tool to run `python drive_client.py download <urls>`
- Extract URLs/IDs from user message using regex or string search
- Pass all URLs/IDs to the script in a single command
- The script handles URL to ID conversion automatically
- After download, offer to work with files based on user's original request
- Remember that files are saved to visible `drive_files/` directory
- Use Read tool to access files if user wants analysis
