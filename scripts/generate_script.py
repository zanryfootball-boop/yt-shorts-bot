import json
import random
import os
from datetime import datetime
from groq import Groq

NICHES = [
    "motivational football quotes",
    "football success mindset",
    "football legends inspiration",
    "never give up football motivation",
    "football dedication and hardwork",
    "football teamwork quotes",
    "football champions mindset",
    "football dreams and goals",
    "football passion and hunger",
    "football greatness quotes",
]

BACKGROUNDS = [
    "stadium_lights",
    "football_pitch",
    "crowd_energy",
    "goal_celebration",
    "training_ground",
    "trophy_glory",
    "player_silhouette",
    "ball_particles",
]

def generate_script():
    api_key = "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"
    client = Groq(api_key=api_key)
    niche = random.choice(NICHES)
    background = random.choice(BACKGROUNDS)
    slot = "morning" if datetime.now().hour < 12 else "evening"
    prompt = (
        "You are a viral YouTube Shorts script writer specializing in football motivation. "
        "Write a 60-second motivational script for a Short about: " + niche + "\n\n"
        "The video is for the " + slot + " audience.\n\n"
        "Use powerful football quotes, mention legends like Ronaldo, Messi, Pele, Zidane etc.\n"
        "Make it emotional, powerful and inspiring.\n\n"
        "Return ONLY valid JSON with this exact structure:\n"
        "{\n"
        '  "title": "YouTube title (max 70 chars, football motivation)",\n'
        '  "description": "YouTube description (2-3 sentences + hashtags like #football #motivation #shorts)",\n'
        '  "tags": ["football", "motivation", "shorts", "footballquotes", "inspire"],\n'
        '  "hook": "First 3 seconds hook line (must grab attention instantly)",\n'
        '  "lines": [\n'
        '    "Line 1 of narration (short, punchy, motivational)",\n'
        '    "Line 2",\n'
        '    "Line 3",\n'
        '    "Line 4",\n'
        '    "Line 5",\n'
        '    "Line 6",\n'
        '    "Line 7 - powerful closing line + follow for more"\n'
        '  ],\n'
        '  "background_style": "' + background + '",\n'
        '  "color_theme": "one of: champions_gold|pitch_green|stadium_night|fire_red|royal_blue"
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
