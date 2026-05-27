"""
get_refresh_token.py  —  Run this ONCE on your local machine.

This script opens a browser, asks you to sign in to Google,
and prints the refresh token you need to add to GitHub Secrets.

Usage:
  pip install google-auth-oauthlib
  python get_refresh_token.py

You'll need:
  - Your OAuth 2.0 Client ID
  - Your OAuth 2.0 Client Secret
  (Get these from https://console.cloud.google.com → APIs & Services → Credentials)
"""

import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

CLIENT_ID     = input("Paste your OAuth Client ID: ").strip()
CLIENT_SECRET = input("Paste your OAuth Client Secret: ").strip()

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=0)

print("\n" + "="*60)
print("SUCCESS! Add these to GitHub Secrets:")
print("="*60)
print(f"YT_CLIENT_ID     = {CLIENT_ID}")
print(f"YT_CLIENT_SECRET = {CLIENT_SECRET}")
print(f"YT_REFRESH_TOKEN = {creds.refresh_token}")
print("="*60)
