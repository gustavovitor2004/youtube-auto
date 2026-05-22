"""Faz upload TikTok dos videos com temas distintos prontos."""
import sys, json, os
if hasattr(sys.stdout,'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr,'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path
from modules.ffmpeg_helper import ensure_ffmpeg
ensure_ffmpeg()
from modules.tiktok_uploader import TikTokUploader
from config import Config

cfg = Config()
tt = TikTokUploader(cfg)

# Videos distintos prontos para TikTok
UPLOADS = [
    {
        "mp4": "output/20260522_164602_shorts.mp4",
        "title": "You're Hooked On Your Phone",
        "tags": ["phone addiction","dark psychology","dopamine","social media","psychology","mindset","fyp","shorts"],
    },
    {
        "mp4": "output/20260522_164419_shorts.mp4",
        "title": "They're Pretending to Like You",
        "tags": ["dark psychology","toxic people","narcissist","psychology","fake friends","mindset","fyp","shorts"],
    },
    {
        "mp4": "output/20260522_164345_shorts.mp4",
        "title": "What's Really Controlling Your Mind",
        "tags": ["dark psychology","mind control","manipulation","brain","psychology facts","mindset","fyp","shorts"],
    },
]

for i, v in enumerate(UPLOADS):
    mp4 = Path(v["mp4"])
    if not mp4.exists():
        print(f"[{i+1}] SKIP (not found): {mp4}")
        continue
    print(f"\n[{i+1}/3] Uploading: {v['title']}")
    result = tt.upload(
        video_path=mp4,
        title=v["title"],
        description=v["title"],
        tags=v["tags"],
        mode="shorts"
    )
    print(f"  Result: {result}")

print("\n[DONE] TikTok batch upload complete.")
