"""Upload ONE video to TikTok. Called as subprocess for process isolation.
Usage: python _tt_one.py <mp4_path> <title> <tags_json>
Exit 0 = success, Exit 1 = failure.
"""
import sys, json
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path
from modules.ffmpeg_helper import ensure_ffmpeg
ensure_ffmpeg()

from modules.tiktok_uploader import TikTokUploader
from config import Config

mp4   = Path(sys.argv[1])
title = sys.argv[2]
tags  = json.loads(sys.argv[3])

cfg = Config()
tt  = TikTokUploader(cfg)

result = tt.upload(video_path=mp4, title=title, description=title,
                   tags=tags, mode="shorts")
print(f"RESULT:{result}")
sys.exit(0 if result == "tiktok_ok" else 1)
