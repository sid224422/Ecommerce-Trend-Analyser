"""Rename !.env to .env"""
from pathlib import Path
import shutil

src = Path('!.env')
dst = Path('.env')

if src.exists():
    if dst.exists():
        print(f"[INFO] .env already exists, backing up...")
        backup = Path('.env.backup')
        if backup.exists():
            backup.unlink()
        shutil.move(str(dst), str(backup))
    
    shutil.move(str(src), str(dst))
    print(f"[SUCCESS] Renamed !.env to .env")
    print(f"  .env exists: {dst.exists()}")
    print(f"  .env size: {dst.stat().st_size} bytes")
else:
    print(f"[ERROR] !.env file not found")

