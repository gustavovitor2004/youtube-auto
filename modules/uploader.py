"""
YouTube Uploader — 100% gratuito
Usa: YouTube Data API v3 (10.000 unidades/dia gratuitas)
Setup: Google Cloud Console → criar projeto → ativar YouTube API → OAuth2
"""

import pickle
from pathlib import Path

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    GOOGLE_OK = True
except ImportError:
    GOOGLE_OK = False


SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


class YouTubeUploader:
    def __init__(self, config):
        self.config = config
        self._youtube = None

    # ─── PUBLIC ───────────────────────────────────────────────────────────────

    def upload(self, video_path: Path, thumbnail_path: Path,
               title: str, description: str, tags: list[str],
               mode: str) -> str:
        if not GOOGLE_OK:
            print("   [!] google-api-python-client not installed")
            print("   Run: pip install google-api-python-client google-auth-oauthlib")
            return "upload_skipped"

        youtube = self._get_client()
        if not youtube:
            return "auth_failed"

        # Limites do YouTube
        title       = title[:100]
        description = description[:5000]
        tags        = [t[:500] for t in tags[:500]]

        # Para Shorts: adiciona hashtag e mantém título curto
        if mode == "shorts":
            if "#Shorts" not in description:
                description += "\n\n#Shorts #psychology #darkpsychology #mindset"

        body = {
            "snippet": {
                "title":       title,
                "description": description,
                "tags":        tags,
                "categoryId":  self.config.UPLOAD_CATEGORY,
                "defaultLanguage": "en",
            },
            "status": {
                "privacyStatus":           self.config.UPLOAD_PRIVACY,
                "selfDeclaredMadeForKids": False,
            }
        }

        # Upload do vídeo
        print("   Uploading video...")
        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=4 * 1024 * 1024  # 4MB chunks
        )

        req = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )

        video_id = None
        try:
            while video_id is None:
                status, response = req.next_chunk()
                if status:
                    pct = int(status.progress() * 100)
                    print(f"   Uploading... {pct}%", end="\r")
                if response:
                    video_id = response["id"]
        except Exception as e:
            err = str(e)
            if "uploadLimitExceeded" in err:
                print("\n   [!] YouTube daily upload limit reached.")
                print("   Quota resets at midnight Pacific Time. Try again tomorrow.")
                return "quota_exceeded"
            elif "403" in err or "forbidden" in err.lower():
                print(f"\n   [!] YouTube upload forbidden: {err[:120]}")
                return "upload_forbidden"
            else:
                print(f"\n   [!] YouTube upload error: {err[:200]}")
                return "upload_error"

        url = f"https://youtube.com/watch?v={video_id}"
        print(f"\n   [OK] Uploaded: {url}")

        # Thumbnail
        if thumbnail_path and thumbnail_path.exists() and thumbnail_path.stat().st_size > 100:
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(str(thumbnail_path))
                ).execute()
                print("   ✓ Thumbnail set")
            except Exception as e:
                if "403" in str(e) or "forbidden" in str(e).lower():
                    print("   ⚠️  Thumbnail: verify your YouTube account (phone) to enable custom thumbnails")
                else:
                    print(f"   ⚠️  Thumbnail failed: {e}")

        return url

    # ─── AUTH ─────────────────────────────────────────────────────────────────

    def _get_client(self):
        if self._youtube:
            return self._youtube

        token_path   = Path("token.pickle")
        secrets_path = Path(self.config.YOUTUBE_CLIENT_SECRETS)

        if not secrets_path.exists():
            print(f"\n   ❌ client_secrets.json not found!")
            print("   Follow SETUP.md → YouTube API section to create it.")
            return None

        creds = None
        if token_path.exists():
            with open(token_path, "rb") as f:
                creds = pickle.load(f)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(secrets_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(token_path, "wb") as f:
                pickle.dump(creds, f)

        self._youtube = build("youtube", "v3", credentials=creds)
        return self._youtube
