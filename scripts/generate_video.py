import json
import math
import os
import random
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
FPS = 30

COLOR_THEMES = {
    "champions_gold":  {"bg": (10, 8, 0),   "accent": (255, 200, 0),   "text": (255, 255, 255), "sub": (255, 220, 80),  "glow": (255, 180, 0)},
    "pitch_green":     {"bg": (0, 20, 0),   "accent": (0, 220, 80),    "text": (255, 255, 255), "sub": (100, 255, 150), "glow": (0, 180, 60)},
    "stadium_night":   {"bg": (5, 5, 20),   "accent": (255, 255, 255), "text": (255, 255, 255), "sub": (200, 200, 255), "glow": (100, 100, 255)},
    "fire_red":        {"bg": (20, 0, 0),   "accent": (255, 50, 0),    "text": (255, 255, 255), "sub": (255, 120, 60),  "glow": (255, 30, 0)},
    "royal_blue":      {"bg": (0, 5, 30),   "accent": (0, 100, 255),   "text": (255, 255, 255), "sub": (100, 180, 255), "glow": (0, 80, 255)},
}

def get_font(size, bold=True):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def get_audio_duration(audio_path):
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ], capture_output=True, text=True)
    return float(result.stdout.strip())

def draw_glow_text(draw, text, font, x, y, text_color, glow_color):
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            if dx != 0 or dy != 0:
                alpha = max(0, 120 - (abs(dx) + abs(dy)) * 15)
                gc = (glow_color[0], glow_color[1], glow_color[2])
                draw.text((x + dx, y + dy), text, font=font, fill=gc)
    draw.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=text_color)

def make_stadium_lights(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (5, 5, 15))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(42)
    for _ in range(40):
        lx = rng.randint(0, WIDTH)
        ly = rng.randint(0, HEIGHT // 3)
        radius = rng.randint(80, 220)
        flicker = (math.sin(t * rng.uniform(1, 3) + rng.uniform(0, 6)) + 1) / 2
        brightness = int(200 * flicker)
        for r in range(radius, 0, -15):
            alpha = int((brightness * r) / radius)
            color = (min(255, alpha + 100), min(255, alpha + 80), min(255, alpha + 20))
            draw.ellipse([lx - r, ly - r, lx + r, ly + r], fill=color)
    for y in range(HEIGHT // 2, HEIGHT, 5):
        green = int(35 + 25 * math.sin(y * 0.05 + t * 0.3))
        draw.line([(0, y), (WIDTH, y)], fill=(0, green, 0), width=5)
    for i in range(0, WIDTH, 80):
        draw.line([(i, HEIGHT // 2), (i, HEIGHT)], fill=(30, 30, 30), width=1)
    return img

def make_football_pitch(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 100, 0))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    for i in range(0, WIDTH, 60):
        shade = int(20 * math.sin(i * 0.1 + t * 0.2))
        color = (0, max(0, min(255, 100 + shade)), 0)
        draw.rectangle([i, 0, i + 30, HEIGHT], fill=color)
    draw.ellipse([WIDTH // 2 - 220, HEIGHT // 2 - 220, WIDTH // 2 + 220, HEIGHT // 2 + 220], outline=(255, 255, 255), width=6)
    draw.line([(0, HEIGHT // 2), (WIDTH, HEIGHT // 2)], fill=(255, 255, 255), width=6)
    draw.line([(0, 10), (WIDTH, 10)], fill=(255, 255, 255), width=6)
    draw.line([(0, HEIGHT - 10), (WIDTH, HEIGHT - 10)], fill=(255, 255, 255), width=6)
    draw.rectangle([WIDTH // 2 - 6, HEIGHT // 2 - 6, WIDTH // 2 + 6, HEIGHT // 2 + 6], fill=(255, 255, 255))
    bx = int(WIDTH // 2 + 180 * math.sin(t * 1.2))
    by = int(HEIGHT // 2 + 120 * math.cos(t * 0.8))
    draw.ellipse([bx - 28, by - 28, bx + 28, by + 28], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
    for i in range(4):
        angle = i * math.pi / 2 + t
        lx = bx + int(18 * math.cos(angle))
        ly = by + int(18 * math.sin(angle))
        draw.line([(bx, by), (lx, ly)], fill=(0, 0, 0), width=2)
    return img

def make_crowd_energy(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 10, 30))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(77)
    for _ in range(500):
        px = rng.randint(0, WIDTH)
        py = rng.randint(0, int(HEIGHT * 0.65))
        size = rng.randint(4, 16)
        wave = math.sin(t * rng.uniform(1, 4) + px * 0.01)
        brightness = int(120 + 100 * (wave + 1) / 2)
        colors = [(255, brightness, 0), (255, 0, 0), (0, 50, 255), (255, 255, 255), (0, 255, 50)]
        color = rng.choice(colors)
        draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
    for y in range(int(HEIGHT * 0.65), HEIGHT, 5):
        green = int(60 + 25 * math.sin(y * 0.05 + t * 0.3))
        draw.line([(0, y), (WIDTH, y)], fill=(0, green, 0), width=5)
    return img

def make_goal_celebration(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (5, 5, 20))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(55)
    for _ in range(250):
        px = rng.randint(0, WIDTH)
        start_y = rng.randint(-HEIGHT, 0)
        speed = rng.uniform(100, 300)
        py = int((start_y + t * speed) % HEIGHT)
        size = rng.randint(6, 20)
        colors = [(255, 215, 0), (255, 165, 0), (255, 255, 255), (255, 50, 50), (50, 255, 50), (50, 150, 255)]
        color = rng.choice(colors)
        angle = t * rng.uniform(1, 5)
        x1 = px + int(size * math.cos(angle))
        y1 = py + int(size * math.sin(angle))
        draw.line([(px, py), (x1, y1)], fill=color, width=4)
    pulse = int(50 + 30 * math.sin(t * 3))
    for r in range(pulse * 5, 0, -30):
        alpha = int(40 * r / (pulse * 5))
        draw.ellipse([WIDTH // 2 - r, HEIGHT // 2 - r, WIDTH // 2 + r, HEIGHT // 2 + r],
                     outline=(255, 215, 0), width=3)
    return img

def make_training_ground(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 80, 0))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    for i in range(0, WIDTH, 80):
        shade = int(20 * math.sin(i * 0.08 + t * 0.15))
        color = (0, max(0, min(255, 80 + shade)), 0)
        draw.rectangle([i, 0, i + 40, HEIGHT], fill=color)
    for i in range(6):
        cx = int(WIDTH * (i + 1) / 7)
        cy = int(HEIGHT * 0.35 + 70 * math.sin(t * 0.5 + i))
        draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(255, 165, 0), outline=(0, 0, 0), width=3)
    accent = theme["accent"]
    for i in range(4):
        y = int(HEIGHT * (0.5 + i * 0.12))
        draw.line([(80, y), (WIDTH - 80, y)], fill=accent, width=4)
    return img

def make_trophy_glory(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 8, 2))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(33)
    for _ in range(150):
        px = rng.randint(0, WIDTH)
        py = rng.randint(0, HEIGHT)
        size = rng.uniform(1, 6)
        twinkle = (math.sin(t * rng.uniform(1, 5) + rng.uniform(0, 6)) + 1) / 2
        brightness = int(255 * twinkle)
        draw.ellipse([px - size, py - size, px + size, py + size],
                     fill=(brightness, int(brightness * 0.85), 0))
    cx, cy = WIDTH // 2, HEIGHT // 2
    for r in range(300, 0, -15):
        glow = int(40 * r / 300)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=(min(255, glow + 25), min(255, int(glow * 0.85)), 0))
    return img

def make_player_silhouette(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    for y in range(HEIGHT):
        factor = y / HEIGHT
        r = int(theme["bg"][0] + (theme["accent"][0] - theme["bg"][0]) * factor * 0.6)
        g = int(theme["bg"][1] + (theme["accent"][1] - theme["bg"][1]) * factor * 0.6)
        b = int(theme["bg"][2] + (theme["accent"][2] - theme["bg"][2]) * factor * 0.6)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    cx = WIDTH // 2
    cy = int(HEIGHT * 0.55 + 25 * math.sin(t * 0.8))
    kick_angle = math.sin(t * 1.5) * 0.5
    draw.ellipse([cx - 50, cy - 300, cx + 50, cy - 200], fill=(20, 20, 20))
    draw.rectangle([cx - 40, cy - 200, cx + 40, cy - 60], fill=(20, 20, 20))
    draw.line([(cx - 40, cy - 140), (cx - 90, cy - 80)], fill=(20, 20, 20), width=25)
    draw.line([(cx + 40, cy - 140), (cx + 90, cy - 80)], fill=(20, 20, 20), width=25)
    leg1_x = cx + int(60 * math.sin(kick_angle))
    draw.line([(cx, cy - 60), (leg1_x, cy + 100)], fill=(20, 20, 20), width=25)
    draw.line([(cx, cy - 60), (cx - 40, cy + 100)], fill=(20, 20, 20), width=25)
    bx = leg1_x + int(40 * math.sin(kick_angle + 0.5))
    by = cy + 100
    draw.ellipse([bx - 25, by - 25, bx + 25, by + 25], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
    return img

def make_ball_particles(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(88)
    for _ in range(25):
        bx = int((rng.randint(0, WIDTH) + t * rng.uniform(30, 120)) % WIDTH)
        by = int((rng.randint(0, HEIGHT) + t * rng.uniform(15, 70)) % HEIGHT)
        size = rng.randint(25, 70)
        alpha = rng.uniform(0.3, 0.9)
        color = tuple(int(c * alpha) for c in theme["accent"])
        draw.ellipse([bx - size, by - size, bx + size, by + size],
                     fill=color, outline=(255, 255, 255), width=2)
        for i in range(6):
            angle = i * math.pi / 3 + t * rng.uniform(0.5, 2)
            lx = bx + int(size * 0.7 * math.cos(angle))
            ly = by + int(size * 0.7 * math.sin(angle))
            draw.line([(bx, by), (lx, ly)], fill=(255, 255, 255), width=2)
    return img

BG_MAKERS = {
    "stadium_lights": make_stadium_lights,
    "football_pitch": make_football_pitch,
    "crowd_energy": make_crowd_energy,
    "goal_celebration": make_goal_celebration,
    "training_ground": make_training_ground,
    "trophy_glory": make_trophy_glory,
    "player_silhouette": make_player_silhouette,
    "ball_particles": make_ball_particles,
}

def get_current_word(timestamps, t):
    for item in timestamps:
        if item["start"] <= t <= item["end"]:
            return item["word"]
    return None

def render_frame(frame_idx, script, theme, timestamps, total_frames, font_word, font_hook, font_small):
    bg_style = script.get("background_style", "stadium_lights")
    maker = BG_MAKERS.get(bg_style, make_stadium_lights)
    img = maker(frame_idx, theme)
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS

    current_word = get_current_word(timestamps, t)
    is_first_word = t < (timestamps[2]["end"] if len(timestamps) > 2 else 3)

    if current_word:
        font = font_hook if is_first_word else font_word
        w = draw.textlength(current_word.upper(), font=font)
        x = (WIDTH - w) // 2
        y = HEIGHT // 2 - font.size // 2
        pad = 30
        draw.rounded_rectangle(
            [x - pad, y - pad, x + w + pad, y + font.size + pad],
            radius=20, fill=(0, 0, 0)
        )
        draw_glow_text(draw, current_word.upper(), font, x, y, theme["text"], theme["glow"])

    progress = min(t / (total_frames / FPS), 1.0)
    bar_h = 10
    draw.rectangle([0, HEIGHT - bar_h, WIDTH, HEIGHT], fill=(30, 30, 30))
    draw.rectangle([0, HEIGHT - bar_h, int(WIDTH * progress), HEIGHT], fill=theme["accent"])

    title_font = font_small
    title = script.get("title", "")[:50]
    tw = draw.textlength(title, font=title_font)
    tx = (WIDTH - tw) // 2
    draw.text((tx + 2, 62), title, font=title_font, fill=(0, 0, 0))
    draw.text((tx, 60), title, font=title_font, fill=theme["sub"])

    return img

def generate_video(script_path="script.json", audio_path="narration.mp3", timestamps_path="timestamps.json", output_path="short.mp4"):
    with open(script_path) as f:
        script = json.load(f)
    with open(timestamps_path) as f:
        timestamps = json.load(f)

    theme = COLOR_THEMES.get(script.get("color_theme", "champions_gold"), COLOR_THEMES["champions_gold"])

    font_word = get_font(96)
    font_hook = get_font(110)
    font_small = get_font(42)

    audio_duration = get_audio_duration(audio_path)
    print("[INFO] Audio duration: " + str(round(audio_duration, 2)) + "s")

    total_frames = int(audio_duration * FPS) + FPS
    frames_dir = tempfile.mkdtemp()

    print("[INFO] Rendering " + str(total_frames) + " frames...")
    for i in range(total_frames):
        if i % (FPS * 5) == 0:
            print("  Frame " + str(i) + "/" + str(total_frames))
        frame = render_frame(i, script, theme, timestamps, total_frames, font_word, font_hook, font_small)
        frame.save(os.path.join(frames_dir, "frame_{:05d}.png".format(i)))

    video_no_audio = output_path.replace(".mp4", "_noaudio.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "frame_%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
        video_no_audio
    ], check=True)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_no_audio,
        "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac",
        "-shortest", output_path
    ], check=True)
    os.remove(video_no_audio)

    print("[OK] Video saved: " + output_path)
    return output_path

if __name__ == "__main__":
    generate_video()
