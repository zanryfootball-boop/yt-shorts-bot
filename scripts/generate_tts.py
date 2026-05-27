"""
generate_tts.py
Converts the script lines to an MP3 narration using edge-tts (free Microsoft neural TTS).
No API key needed — uses the same engine as Microsoft Edge browser.
"""

import asyncio
import json
import os
import subprocess
import tempfile

import edge_tts

VOICES = {
    "blue_purple":  "en-US-GuyNeural",
    "red_orange":   "en-US-ChristopherNeural",
    "green_teal":   "en-GB-RyanNeural",
    "gold_white":   "en-AU-WilliamNeural",
    "pink_purple":  "en-US-JennyNeural",
}

async def synthesize(text: str, voice: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice, rate="+10%", pitch="+0Hz")
    await communicate.save(output_path)

def generate_tts(script_path="script.json", output_path="narration.mp3"):
    with open(script_path) as f:
        script = json.load(f)

    voice = VOICES.get(script.get("color_theme", "blue_purple"), "en-US-GuyNeural")
    all_lines = [script["hook"]] + script["lines"]
    full_text = " ... ".join(all_lines)

    print(f"[INFO] Synthesizing with voice: {voice}")
    asyncio.run(synthesize(full_text, voice, output_path))
    print(f"[OK] Narration saved: {output_path}")

if __name__ == "__main__":
    generate_tts()
