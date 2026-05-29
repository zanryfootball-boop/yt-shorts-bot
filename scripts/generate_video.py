import json
import math
import os
import random
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
FPS = 30
FONT_SIZE_HOOK = 76
FONT_SIZE_BODY = 60
FONT_SIZE_SMALL = 44

COLOR_THEMES = {
    "champions_gold":   {"bg": (10, 8, 0),    "accent": (255, 200, 0),   "text": (255, 255, 255), "sub": (255, 220, 80)},
    "pitch_green":      {"bg": (0, 20, 0),     "accent": (0, 220, 80),    "text": (255, 255, 255), "sub": (100, 255, 150)},
    "stadium_night":    {"bg": (5, 5, 20),     "accent": (255, 255, 255), "text": (255, 255, 255), "sub": (200, 200, 255)},
    "fire_red":         {"bg": (20, 0, 0),     "accent": (255, 50, 0),    "text": (255, 255, 255), "sub": (255, 120, 60)},
    "royal_blue":       {"bg": (0, 5, 30),     "accent": (0, 100, 255),   "text": (255, 255, 255), "sub": (100, 180, 255)},
}

def get_font(size):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]:
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

def wrap_text(text, draw, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_text_centered(draw, lines, font, y_start, color, shadow_color=(0, 0, 0), line_height=None):
    lh = line_height or (font.size + 14)
    for i, line in enumerate(lines):
        w = draw.textlength(line, font=font)
        x = (WIDTH - w) // 2
        y = y_start + i * lh
        draw.text((x + 3, y + 3), line, font=font, fill=shadow_color)
        draw.text((x, y), line, font=font, fill=color)

def make_stadium_lights(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (5, 5, 15))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(42)
    for _ in range(30):
        lx = rng.randint(0, WIDTH)
        ly = rng.randint(0, HEIGHT // 3)
        radius = rng.randint(60, 200)
        flicker = (math.sin(t * rng.uniform(1, 3) + rng.uniform(0, 6)) + 1) / 2
        brightness = int(180 * flicker)
        for r in range(radius, 0, -20):
            alpha = int((brightness * r) / radius)
            color = (min(255, alpha + 80), min(255, alpha + 60), min(255, alpha))
            draw.ellipse([lx - r, ly - r, lx + r, ly + r], fill=color)
    for y in range(HEIGHT // 2, HEIGHT, 6):
        green = int(30 + 25 * math.sin(y * 0.05 + t * 0.3))
        draw.line([(0, y), (WIDTH, y)], fill=(0, green, 0), width=6)
    for i in range(0, WIDTH, 80):
        alpha = int(20 + 10 * math.sin(t + i * 0.1))
        draw.line([(i, HEIGHT // 2), (i, HEIGHT)], fill=(200, 200, 200), width=1)
    return img

def make_football_pitch(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 90, 0))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    for i in range(0, WIDTH, 60):
        shade = int(15 * math.sin(i * 0.1 + t * 0.2))
        color = (0, max(0, min(255, 90 + shade)), 0)
        draw.rectangle([i, 0, i + 30, HEIGHT], fill=color)
    draw.ellipse([WIDTH // 2 - 200, HEIGHT // 2 - 200, WIDTH // 2 + 200, HEIGHT // 2 + 200], outline=(255, 255, 255), width=5)
    draw.line([(0, HEIGHT // 2), (WIDTH, HEIGHT // 2)], fill=(255, 255, 255), width=5)
    draw.line([(0, 10), (WIDTH, 10)], fill=(255, 255, 255), width=5)
    draw.line([(0, HEIGHT - 10), (WIDTH, HEIGHT - 10)], fill=(255, 255, 255), width=5)
    draw.rectangle([WIDTH // 2 - 5, HEIGHT // 2 - 5, WIDTH // 2 + 5, HEIGHT // 2 + 5], fill=(255, 255, 255))
    bx = int(WIDTH // 2 + 150 * math.sin(t * 1.2))
    by = int(HEIGHT // 2 + 100 * math.cos(t * 0.8))
    draw.ellipse([bx - 25, by - 25, bx + 25, by + 25], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    return img

def make_crowd_energy(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 10, 30))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(77)
    for _ in range(400):
        px = rng.randint(0, WIDTH)
        py = rng.randint(0, int(HEIGHT * 0.65))
        size = rng.randint(3, 14)
        wave = math.sin(t * rng.uniform(1, 4) + px * 0.01)
        brightness = int(120 + 100 * (wave + 1) / 2)
        colors = [(255, brightness, 0), (255, 0, 0), (0, 0, 255), (255, 255, 255), (0, 255, 0)]
        color = rng.choice(colors)
        draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
    for y in range(int(HEIGHT * 0.65), HEIGHT, 6):
        green = int(50 + 20 * math.sin(y * 0.05 + t * 0.3))
        draw.line([(0, y), (WIDTH, y)], fill=(0, green, 0), width=6)
    return img

def make_goal_celebration(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (5, 5, 20))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(55)
    for _ in range(200):
        px = rng.randint(0, WIDTH)
        start_y = rng.randint(-HEIGHT, 0)
        speed = rng.uniform(80, 250)
        py = int((start_y + t * speed) % HEIGHT)
        size = rng.randint(5, 18)
        colors = [(255, 215, 0), (255, 165, 0), (255, 255, 255), (255, 50, 50), (50, 255, 50)]
        color = rng.choice(colors)
        angle = t * rng.uniform(1, 5)
        x1 = px + int(size * math.cos(angle))
        y1 = py + int(size * math.sin(angle))
        draw.line([(px, py), (x1, y1)], fill=color, width=3)
    pulse = int(40 + 25 * math.sin(t * 3))
    draw.ellipse([WIDTH // 2 - pulse * 5, HEIGHT // 2 - pulse * 5,
                  WIDTH // 2 + pulse * 5, HEIGHT // 2 + pulse * 5],
                 outline=(255, 215, 0), width=4)
    return img

def make_training_ground(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 70, 0))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    for i in range(0, WIDTH, 80):
        shade = int(20 * math.sin(i * 0.08 + t * 0.15))
        color = (0, max(0, min(255, 70 + shade)), 0)
        draw.rectangle([i, 0, i + 40, HEIGHT], fill=color)
    for i in range(5):
        cx = int(WIDTH * (i + 1) / 6)
        cy = int(HEIGHT * 0.3 + 60 * math.sin(t * 0.5 + i))
        draw.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(255, 165, 0), outline=(0, 0, 0), width=2)
    accent = theme["accent"]
    for i in range(3):
        y = int(HEIGHT * (0.5 + i * 0.15))
        draw.line([(100, y), (WIDTH - 100, y)], fill=accent, width=4)
    return img

def make_trophy_glory(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 8, 2))
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(33)
    for _ in range(100):
        px = rng.randint(0, WIDTH)
        py = rng.randint(0, HEIGHT)
        size = rng.uniform(1, 5)
        twinkle = (math.sin(t * rng.uniform(1, 5) + rng.uniform(0, 6)) + 1) / 2
        brightness = int(220 * twinkle)
        draw.ellipse([px - size, py - size, px + size, py + size],
                     fill=(brightness, int(brightness * 0.85), 0))
    cx, cy = WIDTH // 2, HEIGHT // 2
    for r in range(250, 0, -20):
        glow = int(30 * r / 250)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=(min(255, glow + 20), min(255, int(glow * 0.85)), 0))
    return img

def make_player_silhouette(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    for y in range(HEIGHT):
        factor = y / HEIGHT
        r = int(theme["bg"][0] + (theme["accent"][0] - theme["bg"][0]) * factor * 0.5)
        g = int(theme["bg"][1] + (theme["accent"][1] - theme["bg"][1]) * factor * 0.5)
        b = int(theme["bg"][2] + (theme["accent"][2] - theme["bg"][2]) * factor * 0.5)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    cx = WIDTH // 2
    cy = int(HEIGHT * 0.55 + 20 * math.sin(t * 0.8))
    kick_angle = math.sin(t * 1.5) * 0.5
    draw.ellipse([cx - 45, cy - 290, cx + 45, cy - 200], fill=(20, 20, 20))
    draw.rectangle([cx - 35, cy - 200, cx + 35, cy - 60], fill=(20, 20, 20))
    leg1_x = cx + int(50 * math.sin(kick_angle))
    draw.line([(cx, cy - 60), (leg1_x, cy + 90)], fill=(20, 20, 20), width=22)
    draw.line([(cx, cy - 60), (cx - 35, cy + 90)], fill=(20, 20, 20), width=22)
    bx = leg1_x + int(35 * math.sin(kick_angle + 0.5))
    by = cy + 90
    draw.ellipse([bx - 22, by - 22, bx + 22, by + 22], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    return img

def make_ball_particles(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(88)
    for _ in range(20):
        bx = int((rng.randint(0, WIDTH) + t * rng.uniform(20, 100)) % WIDTH)
        by = int((rng.randint(0, HEIGHT) + t * rng.uniform(10, 60)) % HEIGHT)
        size = rng.randint(20, 60)
        alpha = rng.uniform(0.3, 0.8)
        color = tuple(int(c * alpha) for c in theme["accent"])
        draw.ellipse([bx - size, by - size, bx + size, by + size],
                     fill=color, outline=(255, 255, 255), width=2)
        for i in range(4):
            angle = i * math.pi / 2 + t
            lx = bx + int(size * 0.6 * math.cos(angle))
            ly = by + int(size * 0.6 * math.sin(angle))
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

def build_subtitle_schedule(timestamps, script):
    all_lines = [script["hook"]] + script["lines"]
    total_words = len(timestamps)
    words_per_line = max(1, total_words // len(all_lines))
    schedule = []
    for i, line in enumerate(all_lines):
        start_idx = i * words_per_line
        end_idx = start_idx + words_per_line if i < len(all_lines) - 1 else total_words
        chunk = timestamps[start_idx:end_idx]
        if chunk:
            schedule.append((chunk[0]["start"], chunk[-1]["end"], line))
    return schedule

def render_frame(frame_idx, script, theme, subtitle_schedule, total_frames, font_hook, font_body, font_small):
    bg_style = script.get("background_style", "stadium_lights")
    maker = BG_MAKERS.get(bg_style, make_stadium_lights)
    img = maker(frame_idx, theme)
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    current_text = None
    is_hook = False
    for i, (start, end, line) in enumerate(subtitle_schedule):
        if start <= t < end:
            current_text = line
            is_hook = (i == 0)
            break
    if current_text:
        font = font_hook if is_hook else font_body
        wrapped = wrap_text(current_text, draw, font, WIDTH - 120)
        lh = font.size + 14
        total_h = len(wrapped) * lh
        y_start = (HEIGHT - total_h) // 2
        draw.rounded_rectangle(
            [60, y_start - 24, WIDTH - 60, y_start + total_h + 24],
            radius=24, fill=(0, 0, 0)
        )
        draw_text_centered(draw, wrapped, font, y_start, theme["text"])
    progress = min(t / (total_frames / FPS), 1.0)
    draw.rectangle([0, HEIGHT - 8, int(WIDTH * progress), HEIGHT], fill=theme["accent"])
    title_lines = wrap_text(script["title"], draw, font_small, WIDTH - 80)[:2]
    draw_text_centered(draw, title_lines, font_small, 60, theme["sub"])
    return img

def generate_video(script_path="script.json", audio_path="narration.mp3", timestamps_path="timestamps.json", output_path="short.mp4"):
    with open(script_path) as f:
        script = json.load(f)
    with open(timestamps_path) as f:
        timestamps = json.load(f)
    theme = COLOR_THEMES.get(script.get("color_theme", "blue_purple"), COLOR_THEMES["blue_purple"])
    font_hook = get_font(FONT_SIZE_HOOK)
    font_body = get_font(FONT_SIZE_BODY)
    font_small = get_font(FONT_SIZE_SMALL)
    audio_duration = get_audio_duration(audio_path)
    print("[INFO] Audio duration: " + str(round(audio_duration, 2)) + "s")
    subtitle_schedule = build_subtitle_schedule(timestamps, script)
    total_frames = int(audio_duration * FPS) + FPS
    frames_dir = tempfile.mkdtemp()
    print("[INFO] Rendering " + str(total_frames) + " frames...")
    for i in range(total_frames):
        if i % (FPS * 5) == 0:
            print("  Frame " + str(i) + "/" + str(total_frames))
        frame = render_frame(i, script, theme, subtitle_schedule, total_frames, font_hook, font_body, font_small)
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
