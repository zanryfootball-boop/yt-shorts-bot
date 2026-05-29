import asyncio
import json
import os
import whisper
import edge_tts

VOICES = {
    "blue_purple": "en-US-GuyNeural",
    "red_orange": "en-US-ChristopherNeural",
    "green_teal": "en-GB-RyanNeural",
    "gold_white": "en-AU-WilliamNeural",
    "pink_purple": "en-US-JennyNeural",
}

async def synthesize(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice, rate="+10%", pitch="+0Hz")
    await communicate.save(output_path)

def generate_tts(script_path="script.json", output_path="narration.mp3"):
    with open(script_path) as f:
        script = json.load(f)
    voice = VOICES.get(script.get("color_theme", "blue_purple"), "en-US-GuyNeural")
    all_lines = [script["hook"]] + script["lines"]
    full_text = " ".join(all_lines)
    print("[INFO] Synthesizing with voice: " + voice)
    asyncio.run(synthesize(full_text, voice, output_path))
    print("[OK] Narration saved: " + output_path)
    print("[INFO] Running Whisper for subtitle timestamps...")
    model = whisper.load_model("base")
    result = model.transcribe(output_path, word_timestamps=True)
    segments = []
    for segment in result["segments"]:
        for word in segment.get("words", []):
            segments.append({
                "word": word["word"].strip(),
                "start": word["start"],
                "end": word["end"]
            })
    with open("timestamps.json", "w") as f:
        json.dump(segments, f, indent=2)
    print("[OK] Timestamps saved with " + str(len(segments)) + " words")

if __name__ == "__main__":
    generate_tts()
