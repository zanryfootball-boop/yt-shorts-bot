import json
import random
import os
from datetime import datetime
from groq import Groq

NICHES = [
    "motivational football quotes",
    "football legends motivational speeches",
    "Ronaldo motivational story",
    "Messi never give up story",
    "football motivation for life",
    "football champions mindset",
    "football dedication and hardwork",
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

COLOR_THEMES = [
    "champions_gold",
    "pitch_green",
    "stadium_night",
    "fire_red",
    "royal_blue",
]

def generate_script():
    api_key = "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"
    client = Groq(api_key=api_key)
    niche = random.choice(NICHES)
    background = random.choice(BACKGROUNDS)
    color_theme = random.choice(COLOR_THEMES)
    slot = "morning" if datetime.now().hour < 12 else "evening"
    prompt = (
        "You are a viral YouTube Shorts script writer specializing in football edits. "
        "Write a 60-second exciting script for a Short about: " + niche + "\n\n"
        "The video is for the " + slot + " audience.\n\n"
        "Make it energetic, hype and exciting like a football edit video.\n"
        "Mention legends like Ronaldo, Messi, Mbappe, Neymar etc.\n\n"
        "Return ONLY valid JSON with this exact structure:\n"
        "{\n"
        '  "title": "YouTube title (max 70 chars, football edits style)",\n'
        '  "description": "YouTube description (2-3 sentences + hashtags like #football #shorts #edit)",\n'
        '  "tags": ["football", "shorts", "edit", "footballedits", "ronaldo"],\n'
        '  "hook": "First 3 seconds hook line (grab attention instantly)",\n'
        '  "lines": [\n'
        '    "Line 1 (short, hype, energetic)",\n'
        '    "Line 2",\n'
        '    "Line 3",\n'
        '    "Line 4",\n'
        '    "Line 5",\n'
        '    "Line 6",\n'
        '    "Line 7 - powerful closing + follow for more"\n'
        '  ],\n'
        '  "background_style": "' + background + '",\n'
        '  "color_theme": "' + color_theme + '"\n'
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
