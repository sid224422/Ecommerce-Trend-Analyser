"""Rename .env to !.env"""
from pathlib import Path
import shutil

src = Path('.env')
dst = Path('!.env')

if src.exists():
    if dst.exists():
        print(f"[INFO] !.env already exists, replacing...")
        dst.unlink()
    
    shutil.move(str(src), str(dst))
    print(f"[SUCCESS] Renamed .env to !.env")
    print(f"  !.env exists: {dst.exists()}")
    print(f"  !.env size: {dst.stat().st_size} bytes")
else:
    print(f"[INFO] .env file not found")
    if dst.exists():
        print(f"  !.env already exists: {dst.exists()}")

