# Environment Setup Guide

This guide explains how to set up environment variables for the AI-Assisted Market Analytics System.

## Quick Setup

### Method 1: Using .env File (Recommended)

1. **Create .env file:**
   ```bash
   python setup_env.py create
   ```

2. **Edit .env file:**
   Open `.env` file in a text editor and replace `your_api_key_here` with your actual Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Get API Key:**
   - Visit: https://ai.google.dev/gemini-api/docs/quickstart
   - Sign in with your Google account
   - Click "Get API Key" and create a new key
   - Copy the key to your `.env` file

4. **Verify Setup:**
   ```bash
   python setup_env.py
   ```

### Method 2: System Environment Variables

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY='your_api_key_here'
```

**Windows CMD:**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY='your_api_key_here'
```

To make it permanent, add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.)

## Security Notes

- ✅ `.env` file is automatically ignored by git (in `.gitignore`)
- ✅ Never commit API keys to version control
- ✅ Use `.env` file for local development
- ✅ Use system environment variables for production

## Verification

After setting up, verify your configuration:

```bash
python setup_env.py
```

Or test the LLM integration:

```bash
python test_llm_comprehensive.py
```

## Troubleshooting

**Issue: "ModuleNotFoundError: No module named 'dotenv'"**
```bash
pip install python-dotenv
```

**Issue: "ValueError: Gemini API key required"**
- Check that `.env` file exists and contains `GEMINI_API_KEY=...`
- Or set system environment variable
- Verify API key is valid

**Issue: "ImportError: google-generativeai package not found"**
```bash
pip install google-generativeai
```

## Files

- `.env` - Your actual environment variables (not tracked by git)
- `env_template.txt` - Template file (safe to commit)
- `setup_env.py` - Setup helper script
- `.gitignore` - Ensures `.env` is not committed

