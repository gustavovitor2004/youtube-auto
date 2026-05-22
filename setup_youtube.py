"""
YouTube API Setup Helper
Run once to authenticate: python setup_youtube.py
"""

import pickle
import sys
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

GUIDE = """
+----------------------------------------------------------+
|          YouTube API Setup — Step by Step                |
+----------------------------------------------------------+

STEP 1 — Create a Google Cloud project:
  https://console.cloud.google.com/projectcreate

STEP 2 — Enable YouTube Data API v3:
  https://console.cloud.google.com/apis/library/youtube.googleapis.com
  (make sure your new project is selected in the top bar)

STEP 3 — Create OAuth2 credentials:
  https://console.cloud.google.com/apis/credentials
  -> Create Credentials -> OAuth client ID
  -> Application type: Desktop app
  -> Name: YouTube Auto (or anything)
  -> Download JSON

STEP 4 — Configure OAuth consent screen (if prompted):
  -> User type: External
  -> Add your Gmail as test user
  -> Scopes: just save and continue

STEP 5 — Place the downloaded file here:
  {secrets_path}
  (rename it to exactly: client_secrets.json)

STEP 6 — Run this script again:
  python setup_youtube.py

+----------------------------------------------------------+
"""


def main():
    secrets_path = Path("client_secrets.json")

    if not secrets_path.exists():
        print(GUIDE.format(secrets_path=Path.cwd() / "client_secrets.json"))
        sys.exit(0)

    print("\nFound client_secrets.json — starting OAuth flow...")
    print("A browser window will open. Log in and allow access.\n")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install",
            "google-api-python-client", "google-auth-oauthlib", "google-auth-httplib2"])
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request

    token_path = Path("token.pickle")
    creds = None

    if token_path.exists():
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if creds and creds.valid:
        print("Already authenticated! token.pickle is valid.")
    elif creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)
        print("Token refreshed successfully.")
    else:
        flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    print("\nAuthentication successful!")
    print("token.pickle saved — upload will work automatically from now on.")
    print("\nTest upload: python main.py --upload")


if __name__ == "__main__":
    main()
