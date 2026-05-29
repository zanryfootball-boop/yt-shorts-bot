import asyncio
import json
import os
import whisper
import edge_tts

VOICES = {
    "champions_gold": "en-US-GuyNeural",
    "pitch_green": "en-GB-RyanNeural",
    "stadium_night": "en-US-ChristopherNeural",
    "fire_red": "en-AU-WilliamNeural",
    "royal_blue": "en-US-GuyNeural",
}

async def synthesize(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice, rate="+5%", pitch="+0Hz")
    await communicate.save(output_path)

def generate_tts(script_path="script.json", output_path="narration.mp3"):
    with open(script_path) as f:
        script = json.load(f)
    voice = VOICES.get(script.get("color_theme", "champions_gold"), "en-US-GuyNeural")
    all_lines = [script["hook"]] + script["lines"]
    full_text = " ".join(all_lines)
    print("[INFO] Synthesizing with voice: " + voice)
    asyncio.run(synthesize(full_text, voice, output_path))
    print("[OK] Narration saved: " + output_path)
    print("[INFO] Running Whisper for word timestamps...")
    model = whisper.load_model("base")
    result = model.transcribe(output_path, word_timestamps=True)
    words = []
    for segment in result["segments"]:
        for word in segment.get("words", []):
            w = word["word"].strip()
            if w:
                words.append({
                    "word": w,
                    "start": round(word["start"], 3),
                    "end": round(word["end"], 3)
                })
    with open("timestamps.json", "w") as f:
        json.dump(words, f, indent=2)
    print("[OK] " + str(len(words)) + " word timestamps saved")

if __name__ == "__main__":
    generate_tts()
