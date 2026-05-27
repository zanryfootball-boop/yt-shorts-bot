"""
run_pipeline.py
Orchestrates the full YouTube Shorts pipeline:
  1. Generate script (Claude AI)
  2. Generate TTS narration (edge-tts)
  3. Generate video with animated background (PIL + FFmpeg)
  4. Upload to YouTube (YouTube Data API v3)
"""

import os
import sys
import traceback
from datetime import datetime

def log(msg):
    ts = datetime.utcnow().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def run():
    log("=== YouTube Shorts Bot Starting ===")

    log("Step 1/4: Generating script...")
    from generate_script import generate_script
    script = generate_script()
    log(f"Topic: {script['niche']} | Title: {script['title']}")

    log("Step 2/4: Generating TTS narration...")
    from generate_tts import generate_tts
    generate_tts()

    log("Step 3/4: Rendering video...")
    from generate_video import generate_video
    generate_video()

    log("Step 4/4: Uploading to YouTube...")
    from upload_to_youtube import upload_video
    video_id = upload_video()

    log(f"=== Done! https://youtube.com/shorts/{video_id} ===")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
