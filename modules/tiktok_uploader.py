"""
TikTok Uploader — 100% gratuito
Usa: tiktok-uploader (automacao via browser)
Setup: python setup_tiktok.py
"""

from pathlib import Path

try:
    from tiktok_uploader.upload import upload_videos
    TIKTOK_OK = True
except ImportError:
    TIKTOK_OK = False


class TikTokUploader:
    COOKIES_FILE = "tiktok_cookies.txt"

    def __init__(self, config):
        self.config = config

    def upload(self, video_path: Path, title: str,
               description: str, tags: list, mode: str = "shorts") -> str:

        if not TIKTOK_OK:
            print("   [!] tiktok-uploader not installed")
            print("   Run: pip install tiktok-uploader")
            return "not_installed"

        cookies = Path(self.COOKIES_FILE)
        if not cookies.exists():
            print(f"   [X] {self.COOKIES_FILE} not found -- run: python setup_tiktok.py")
            return "no_cookies"

        # Monta descrição TikTok: título + hashtags
        clean_tags = [t.replace(" ", "").replace("#", "") for t in tags[:6]]
        hashtags = " ".join(f"#{t}" for t in clean_tags)
        hashtags += " #darkpsychology #psychology #mindset #fyp #shorts"
        tiktok_desc = f"{title}\n\n{hashtags}"[:2200]

        try:
            print("   Uploading to TikTok (opening browser)...")
            videos = [{"path": str(video_path), "description": tiktok_desc}]
            upload_videos(videos=videos, cookies=str(cookies), browser="chrome")
            print("   [OK] Uploaded to TikTok!")
            return "tiktok_ok"
        except Exception as e:
            print(f"   [X] TikTok upload failed: {e}")
            print("   Tip: cookies may have expired -- run: python setup_tiktok.py")
            return "failed"
