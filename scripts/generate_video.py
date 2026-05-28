import json
import math
import os
import random
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
FPS = 30
FONT_SIZE_HOOK = 72
FONT_SIZE_BODY = 58
FONT_SIZE_SMALL = 44

COLOR_THEMES = {
    "blue_purple":  {"bg": (10, 5, 40),   "accent": (100, 80, 255), "text": (255, 255, 255), "sub": (180, 160, 255)},
    "red_orange":   {"bg": (30, 5, 5),    "accent": (255, 80, 30),  "text": (255, 255, 255), "sub": (255, 160, 100)},
    "green_teal":   {"bg": (5, 25, 20),   "accent": (30, 200, 150), "text": (255, 255, 255), "sub": (100, 230, 190)},
    "gold_white":   {"bg": (20, 15, 5),   "accent": (220, 180, 50), "text": (255, 255, 255), "sub": (230, 210, 130)},
    "pink_purple":  {"bg": (25, 5, 25),   "accent": (220, 60, 180), "text": (255, 255, 255), "sub": (200, 130, 220)},
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
        w = draw.textlength(test, font=font)
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_text_centered(draw, lines, font, y_start, color, shadow_color=(0, 0, 0), line_height=None):
    lh = line_height or (font.size + 12)
    for i, line in enumerate(lines):
        w = draw.textlength(line, font=font)
        x = (WIDTH - w) // 2
        y = y_start + i * lh
        draw.text((x + 3, y + 3), line, font=font, fill=shadow_color)
        draw.text((x, y), line, font=font, fill=color)

def make_background_particles(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    rng = random.Random(42)
    t = frame_idx / FPS
    for _ in range(120):
        px = rng.randint(0, WIDTH)
        py = rng.randint(0, HEIGHT)
        speed = rng.uniform(0.3, 1.5)
        size = rng.randint(2, 8)
        phase = rng.uniform(0, math.pi * 2)
        ox = int(math.sin(t * speed + phase) * 30)
        oy = int((t * speed * 60) % HEIGHT)
        nx = (px + ox) % WIDTH
        ny = (py + oy) % HEIGHT
        alpha_factor = (math.sin(t * speed * 2 + phase) + 1) / 2
        color = tuple(int(c * alpha_factor) for c in theme["accent"])
        draw.ellipse([nx - size, ny - size, nx + size, ny + size], fill=color)
    return img

def make_background_waves(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    for layer in range(4):
        amp = 60 + layer * 20
        freq = 0.003 + layer * 0.001
        speed = 0.8 + layer * 0.3
        phase = layer * math.pi / 2
        alpha = 0.3 + layer * 0.15
        color = tuple(int(c * alpha) for c in theme["accent"])
        pts = []
        for x in range(0, WIDTH + 10, 10):
            y = int(HEIGHT * (0.3 + layer * 0.15) + amp * math.sin(freq * x + t * speed + phase))
            pts.append((x, y))
        pts += [(WIDTH, HEIGHT), (0, HEIGHT)]
        draw.polygon(pts, fill=color)
    return img

def make_background_geometric(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(99)
    for i in range(20):
        cx = rng.randint(100, WIDTH - 100)
        cy = rng.randint(100, HEIGHT - 100)
        size = rng.randint(40, 180)
        rot = t * rng.uniform(0.3, 1.2) + rng.uniform(0, math.pi)
        alpha = rng.uniform(0.1, 0.35)
        color = tuple(int(c * alpha) for c in theme["accent"])
        pts = []
        sides = rng.choice([3, 4, 6])
        for s in range(sides):
            angle = rot + s * (2 * math.pi / sides)
            pts.append((cx + size * math.cos(angle), cy + size * math.sin(angle)))
        draw.polygon(pts, outline=color, width=2)
    return img

def make_background_starfield(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    rng = random.Random(7)
    for _ in range(200):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, HEIGHT)
        speed = rng.uniform(0.2, 2.0)
        size = rng.uniform(0.5, 3.0)
        phase = rng.uniform(0, math.pi * 2)
        brightness = int(180 + 75 * math.sin(t * speed + phase))
        brightness = max(0, min(255, brightness))
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(brightness, brightness, brightness))
    return img

def make_background_gradient_flow(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    for y in range(0, HEIGHT, 4):
        factor = (math.sin(y * 0.003 + t * 0.5) + 1) / 2
        r = int(theme["bg"][0] + (theme["accent"][0] - theme["bg"][0]) * factor * 0.5)
        g = int(theme["bg"][1] + (theme["accent"][1] - theme["bg"][1]) * factor * 0.5)
        b = int(theme["bg"][2] + (theme["accent"][2] - theme["bg"][2]) * factor * 0.5)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b), width=4)
    return img

BG_MAKERS = {
    "particles": make_background_particles,
    "waves": make_background_waves,
    "geometric": make_background_geometric,
    "starfield": make_background_starfield,
    "gradient_flow": make_background_gradient_flow,
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
    bg_style = script.get("background_style", "particles")
    maker = BG_MAKERS.get(bg_style, make_background_particles)
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
        draw.rounded_rectangle([60, y_start - 24, WIDTH - 60, y_start + total_h + 24], radius=24, fill=(0, 0, 0))
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
