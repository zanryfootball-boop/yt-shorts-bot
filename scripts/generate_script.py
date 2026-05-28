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

def generate_script():
    api_key = "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"
    client = Groq(api_key=api_key)
    niche = random.choice(NICHES)
    slot = "morning" if datetime.now().hour < 12 else "evening"
    prompt = (
        "You are a viral YouTube Shorts script writer. "
        "Write a 60-second script for a Short about: " + niche + "\n\n"
        "The video is for the " + slot + " audience.\n\n"
        "Return ONLY valid JSON with this exact structure:\n"
        "{\n"
        '  "title": "YouTube title (max 70 chars, no clickbait)",\n'
        '  "description": "YouTube description (2-3 sentences + hashtags)",\n'
        '  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],\n'
        '  "hook": "First 3 seconds hook line (must grab attention instantly)",\n'
        '  "lines": [\n'
        '    "Line 1 of narration (short, punchy)",\n'
        '    "Line 2",\n'
        '    "Line 3",\n'
        '    "Line 4",\n'
        '    "Line 5",\n'
        '    "Line 6",\n'
        '    "Line 7 - call to action (follow for more)"\n'
        '  ],\n'
        '  "background_style": "one of: particles|waves|geometric|gradient_flow|starfield",\n'
        '  "color_theme": "one of: blue_purple|red_orange|green_teal|gold_white|pink_purple"\n'
        "}"
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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
    print("[OK] Script generated: " + script["title"])
    return script

if __name__ == "__main__":
    generate_script()
