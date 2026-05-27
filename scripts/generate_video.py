"""
generate_video.py
Creates an animated YouTube Short (1080x1920) with:
- Animated background (particles / waves / geometric / starfield / gradient_flow)
- Centered text captions synced to narration timing
- Word-by-word subtitle burn-in
"""

import json
import math
import os
import random
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
FPS = 30
FONT_SIZE_HOOK = 72
FONT_SIZE_BODY = 58
FONT_SIZE_SMALL = 44

COLOR_THEMES = {
    "blue_purple":    {"bg": (10, 5, 40),    "accent": (100, 80, 255), "text": (255, 255, 255), "sub": (180, 160, 255)},
    "red_orange":     {"bg": (30, 5, 5),     "accent": (255, 80, 30),  "text": (255, 255, 255), "sub": (255, 160, 100)},
    "green_teal":     {"bg": (5, 25, 20),    "accent": (30, 200, 150), "text": (255, 255, 255), "sub": (100, 230, 190)},
    "gold_white":     {"bg": (20, 15, 5),    "accent": (220, 180, 50), "text": (255, 255, 255), "sub": (230, 210, 130)},
    "pink_purple":    {"bg": (25, 5, 25),    "accent": (220, 60, 180), "text": (255, 255, 255), "sub": (200, 130, 220)},
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

def wrap_text(text, draw, font, max_width):
    words = text.split()
    lines, current = [], ""
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

def draw_text_centered(draw, lines, font, y_start, color, shadow_color=(0,0,0), line_height=None):
    lh = line_height or (font.size + 12)
    for i, line in enumerate(lines):
        w = draw.textlength(line, font=font)
        x = (WIDTH - w) // 2
        y = y_start + i * lh
        draw.text((x+3, y+3), line, font=font, fill=shadow_color)
        draw.text((x, y), line, font=font, fill=color)

def make_background_particles(frame_idx, total_frames, theme):
    bg = theme["bg"]
    accent = theme["accent"]
    img = Image.new("RGB", (WIDTH, HEIGHT), bg)
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
        color = tuple(int(c * alpha_factor) for c in accent)
        draw.ellipse([nx-size, ny-size, nx+size, ny+size], fill=color)

    return img

def make_background_waves(frame_idx, total_frames, theme):
    bg = theme["bg"]
    accent = theme["accent"]
    img = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS

    for layer in range(4):
        amp = 60 + layer * 20
        freq = 0.003 + layer * 0.001
        speed = 0.8 + layer * 0.3
        phase = layer * math.pi / 2
        alpha = 0.3 + layer * 0.15
        color = tuple(int(c * alpha) for c in accent)

        pts = []
        for x in range(0, WIDTH + 10, 10):
            y = int(HEIGHT * (0.3 + layer * 0.15) + amp * math.sin(freq * x + t * speed + phase))
            pts.append((x, y))
        pts += [(WIDTH, HEIGHT), (0, HEIGHT)]
        draw.polygon(pts, fill=color)

    return img

def make_background_geometric(frame_idx, total_frames, theme):
    bg = theme["bg"]
    accent = theme["accent"]
    img = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS

    rng = random.Random(99)
    for i in range(20):
        cx = rng.randint(100, WIDTH-100)
        cy = rng.randint(100, HEIGHT-100)
        size = rng.randint(40, 180)
        rot = t * rng.uniform(0.3, 1.2) + rng.uniform(0, math.pi)
        alpha = rng.uniform(0.1, 0.35)
        color = tuple(int(c * alpha) for c in accent)
        pts = []
        sides = rng.choice([3, 4, 6])
        for s in range(sides):
            angle = rot + s * (2 * math.pi / sides)
            pts.append((cx + size * math.cos(angle), cy + size * math.sin(angle)))
        draw.polygon(pts, outline=color, width=2)

    return img

def make_background_starfield(frame_idx, total_frames, theme):
    bg = theme["bg"]
    img = Image.new("RGB", (WIDTH, HEIGHT), bg)
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
        draw.ellipse([x-size, y-size, x+size, y+size], fill=(brightness, brightness, brightness))

    return img

def make_background_gradient_flow(frame_idx, total_frames, theme):
    accent = theme["accent"]
    bg = theme["bg"]
    img = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS

    for y in range(0, HEIGHT, 4):
        factor = (math.sin(y * 0.003 + t * 0.5) + 1) / 2
        r = int(bg[0] + (accent[0] - bg[0]) * factor * 0.5)
        g = int(bg[1] + (accent[1] - bg[1]) * factor * 0.5)
        b = int(bg[2] + (accent[2] - bg[2]) * factor * 0.5)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b), width=4)

    return img

BG_MAKERS = {
    "particles": make_background_particles,
    "waves": make_background_waves,
    "geometric": make_background_geometric,
    "starfield": make_background_starfield,
    "gradient_flow": make_background_gradient_flow,
}

def seconds_per_line(script):
    total_lines = len(script["lines"]) + 1
    return 58.0 / total_lines

def render_frame(frame_idx, script, theme, font_hook, font_body, font_small):
    bg_style = script.get("background_style", "particles")
    maker = BG_MAKERS.get(bg_style, make_background_particles)
    img = maker(frame_idx, None, theme)
    draw = ImageDraw.Draw(img)

    t = frame_idx / FPS
    spl = seconds_per_line(script)

    all_lines = [script["hook"]] + script["lines"]
    line_idx = min(int(t / spl), len(all_lines) - 1)
    current_text = all_lines[line_idx]

    is_hook = (line_idx == 0)
    font = font_hook if is_hook else font_body
    max_w = WIDTH - 120

    wrapped = wrap_text(current_text, draw, font, max_w)
    lh = font.size + 14
    total_h = len(wrapped) * lh
    y_start = (HEIGHT - total_h) // 2

    pill_pad = 24
    pill_x0 = 60
    pill_x1 = WIDTH - 60
    pill_y0 = y_start - pill_pad
    pill_y1 = y_start + total_h + pill_pad
    draw.rounded_rectangle([pill_x0, pill_y0, pill_x1, pill_y1], radius=24,
                            fill=(0, 0, 0, 160) if img.mode == "RGBA" else (0, 0, 0))

    draw_text_centered(draw, wrapped, font, y_start, theme["text"])

    progress = t / 60.0
    bar_w = int(WIDTH * progress)
    draw.rectangle([0, HEIGHT - 8, bar_w, HEIGHT], fill=theme["accent"])

    title_font = font_small
    title_lines = wrap_text(script["title"], draw, title_font, WIDTH - 80)[:2]
    draw_text_centered(draw, title_lines, title_font, 60, theme["sub"])

    return img

def generate_video(script_path="script.json", output_path="short.mp4"):
    with open(script_path) as f:
        script = json.load(f)

    theme = COLOR_THEMES.get(script.get("color_theme", "blue_purple"), COLOR_THEMES["blue_purple"])

    font_hook = get_font(FONT_SIZE_HOOK)
    font_body = get_font(FONT_SIZE_BODY)
    font_small = get_font(FONT_SIZE_SMALL)

    total_frames = FPS * 60
    frames_dir = tempfile.mkdtemp()

    print(f"[INFO] Rendering {total_frames} frames...")
    for i in range(total_frames):
        if i % (FPS * 5) == 0:
            print(f"  Frame {i}/{total_frames}")
        frame = render_frame(i, script, theme, font_hook, font_body, font_small)
        frame.save(os.path.join(frames_dir, f"frame_{i:05d}.png"))

    video_no_audio = output_path.replace(".mp4", "_noaudio.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "frame_%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "23", video_no_audio
    ], check=True)

    if os.path.exists("narration.mp3"):
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_no_audio,
            "-i", "narration.mp3",
            "-c:v", "copy", "-c:a", "aac",
            "-shortest", output_path
        ], check=True)
        os.remove(video_no_audio)
    else:
        os.rename(video_no_audio, output_path)

    print(f"[OK] Video saved: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_video()
