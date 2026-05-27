"""
generate_script.py
Picks a trending topic and writes a 60-second YouTube Shorts script using Groq API (free).
"""

import json
import random
import os
from datetime import datetime
from groq import Groq

NICHES = [
    "mind-blowing psychology facts",
    "little-known history facts",
    "space and universe facts",
    "life-changing productivity tips",
    "surprising science facts",
    "ancient civilization secrets",
    "human body facts",
    "bizarre animal behaviors",
    "unsolved mysteries",
    "future technology predictions",
]

def generate_script() -> dict:
    client = Groq(api_key = "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")

    niche = random.choice(NICHES)
    slot = "morning" if datetime.now().hour < 12 else "evening"

    prompt = f"""You are a viral YouTube Shorts script writer. Write a 60-second script for a Short about: {niche}

The video is for the {slot} audience.

Return ONLY valid JSON with this exact structure:
{{
  "title": "YouTube title (max 70 chars, no clickbait)",
  "description": "YouTube description (2-3 sentences + hashtags)",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "hook": "First 3 seconds hook line (must grab attention instantly)",
  "lines": [
    "Line 1 of narration (short, punchy)",
    "Line 2",
    "Line 3",
    "Line 4",
    "Line 5",
    "Line 6",
    "Line 7 - call to action (follow for more)"
  ],
  "background_style": "one of: particles|waves|geometric|gradient_flow|starfield",
  "color_theme": "one of: blue_purple|red_orange|green_teal|gold_white|pink_purple"
}}"""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.9,
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    script = json.loads(raw)
    script["niche"] = niche
    script["generated_at"] = datetime.utcnow().isoformat()

    with open("script.json", "w") as f:
        json.dump(script, f, indent=2)

    print(f"[OK] Script generated: {script['title']}")
    return script

if __name__ == "__main__":
    generate_script()
