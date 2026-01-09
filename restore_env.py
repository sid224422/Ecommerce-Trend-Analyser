"""Restore API key to .env file"""
from pathlib import Path

# The API key we saw earlier
api_key = "AIzaSyBKV56DkmyeG4VvM5X0IDbXrczGwWVCw04"

# Create .env file with the actual key
env_file = Path('.env')
content = f"# Gemini API Key for LLM Summarization\nGEMINI_API_KEY={api_key}\n"

with open(env_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[SUCCESS] .env file created with API key")
print(f"  File size: {env_file.stat().st_size} bytes")
print(f"  Key length: {len(api_key)} characters")

