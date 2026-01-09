# Fix .env File - Quick Guide

## Problem
Your `.env` file exists but is **empty (0 bytes)**. Here's how to fix it:

## Solution

### Method 1: Manual Edit (Recommended)

1. **Open the .env file** in any text editor:
   - Location: `C:\Users\ssid2\OneDrive\Desktop\Final\.env`
   - You can use Notepad, VS Code, or any text editor

2. **Add this exact line** (replace with your actual API key):
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Important Format Rules:**
   - ✅ **CORRECT**: `GEMINI_API_KEY=AIzaSy...`
   - ❌ **WRONG**: `GEMINI_API_KEY = AIzaSy...` (spaces around =)
   - ❌ **WRONG**: `GEMINI_API_KEY="AIzaSy..."` (quotes are optional but can cause issues)
   - ❌ **WRONG**: `GEMINI_API_KEY:AIzaSy...` (use = not :)

4. **Save the file** (Ctrl+S)

5. **Verify it worked:**
   ```bash
   python check_env_format.py
   ```

### Method 2: Using PowerShell Command

If you have your API key ready, run this in PowerShell:

```powershell
# Replace YOUR_ACTUAL_KEY with your real API key
"GEMINI_API_KEY=YOUR_ACTUAL_KEY" | Out-File -FilePath .env -Encoding utf8
```

### Method 3: Create Template and Edit

Run this to create a template file:
```bash
python -c "with open('.env', 'w') as f: f.write('GEMINI_API_KEY=your_api_key_here\n')"
```

Then edit `.env` and replace `your_api_key_here` with your actual key.

## Get Your API Key

1. Visit: https://ai.google.dev/gemini-api/docs/quickstart
2. Sign in with Google account
3. Click "Get API Key"
4. Copy the key
5. Paste it in your `.env` file

## Verify Setup

After saving your `.env` file, run:

```bash
python verify_env.py
```

This will:
- Check if the key loads correctly
- Test the API connection
- Confirm everything works

## Troubleshooting

**If the file still appears empty:**
- Make sure you **saved** the file (Ctrl+S)
- Check if OneDrive is syncing the file (might be a sync delay)
- Try closing and reopening the file
- Check file permissions

**If key is not loading:**
- Make sure there are **no spaces** around the `=` sign
- Make sure the file is named exactly `.env` (not `.env.txt`)
- Make sure the file is in the project root directory

**If API connection fails:**
- Verify your API key is correct
- Check if you have internet connection
- Make sure the API key is active in Google AI Studio

