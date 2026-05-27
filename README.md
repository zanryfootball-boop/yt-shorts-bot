# YouTube Shorts Bot — Fully Automated, Free

Posts 2 AI-generated YouTube Shorts daily at **8:00 AM** and **6:00 PM IST**.

## What it does
- AI picks a trending topic (psychology, science, history, space, etc.)
- Gemini 1.5 Flash writes a punchy 60-second script
- Microsoft Edge TTS narrates it (free, neural voices)
- Animated background rendered from scratch (particles / waves / starfield / etc.)
- Uploaded automatically via YouTube Data API v3

## Cost
| Component | Tool | Cost |
|-----------|------|------|
| Script generation | Gemini 1.5 Flash | Free |
| Text-to-speech | edge-tts (Microsoft) | Free |
| Video rendering | Pillow + FFmpeg | Free |
| Scheduling | GitHub Actions | Free (2000 min/mo) |
| Upload | YouTube Data API | Free |

**Total: $0 / day — completely free**

---

## Setup (one time, ~20 minutes)

### Step 1 — Get Gemini API key (free)
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API Key → Create API Key**
3. Copy the key

### Step 2 — Google Cloud setup for YouTube
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. "yt-shorts-bot")
3. Enable **YouTube Data API v3** (APIs & Services → Enable APIs)
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Application type: **Desktop App**
6. Note your **Client ID** and **Client Secret**

### Step 3 — Get your refresh token
Run this on your local machine (one time only):
```bash
pip install google-auth-oauthlib
python get_refresh_token.py
```
Sign in with your YouTube channel's Google account when the browser opens.
Copy the printed `YT_REFRESH_TOKEN`.

### Step 4 — GitHub repository
1. Fork or create a new GitHub repo
2. Upload all these files to it
3. Go to **Settings → Secrets and Variables → Actions → New secret**

Add these 4 secrets:
| Secret Name | Value |
|-------------|-------|
| `GEMINI_API_KEY` | From aistudio.google.com |
| `YT_CLIENT_ID` | From Google Cloud |
| `YT_CLIENT_SECRET` | From Google Cloud |
| `YT_REFRESH_TOKEN` | From get_refresh_token.py |

### Step 5 — Test it
Go to **Actions tab → Upload YouTube Short → Run workflow**
Watch the logs — your first Short should appear on YouTube in ~5 minutes!

---

## File structure
```
yt-shorts-bot/
├── .github/workflows/
│   └── upload-short.yml      ← GitHub Actions schedule
├── scripts/
│   ├── run_pipeline.py       ← Orchestrator (runs all steps)
│   ├── generate_script.py    ← Gemini AI topic + script
│   ├── generate_tts.py       ← edge-tts narration
│   ├── generate_video.py     ← Animated video renderer
│   └── upload_to_youtube.py  ← YouTube API upload
├── get_refresh_token.py      ← One-time OAuth helper
├── requirements.txt
└── README.md
```

## Customizing topics
Edit the `NICHES` list in `generate_script.py` to target your channel's niche.

## Changing upload times
Edit `.github/workflows/upload-short.yml`.
Times are in UTC. IST = UTC+5:30, so:
- 8:00 AM IST = 2:30 AM UTC → `cron: '30 2 * * *'`
- 6:00 PM IST = 12:30 PM UTC → `cron: '30 12 * * *'`
