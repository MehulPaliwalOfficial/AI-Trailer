"""Synced cinematic renderer for the AI Movie Trailer Generator.

This renderer converts still scene images into a dynamic trailer-style MP4. It
also supports accurate captions when a `caption_timeline.json` file exists next
to the narration audio. The sample project includes that file, created from
separate voice-over segments, so captions match the voice line-by-line.
"""
from __future__ import annotations

import json
import math
import random
import subprocess
import textwrap
from pathlib import Path
from typing import Iterable

import cv2
import imageio_ffmpeg
import numpy as np
from moviepy import AudioFileClip
from PIL import Image, ImageDraw, ImageFont, ImageOps

WIDTH = 1280
HEIGHT = 720
LETTERBOX = 62


def _font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


FONT_CAPTION = _font(31, True)
FONT_SMALL = _font(19, True)
FONT_BIG = _font(78, True)
FONT_TIMER = _font(54, True)
FONT_MID = _font(32, True)

DEFAULT_LABELS = [
    "SAFE CITY",
    "PREDICTION ENGINE",
    "CLASSIFIED TARGET",
    "CHALLENGE THE FUTURE",
    "SYSTEM PURSUIT",
    "EXPOSE THE TRUTH",
    "DESTINY PROGRAMMED",
    "TITLE REVEAL",
]


def _text_size(text: str, font) -> tuple[int, int]:
    image = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(image)
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def _fit_image(path: str | Path) -> np.ndarray:
    image = Image.open(path).convert("RGB")
    image = ImageOps.fit(image, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    return np.array(image)


def _make_vignette() -> np.ndarray:
    y, x = np.ogrid[:HEIGHT, :WIDTH]
    radius = np.sqrt(((x - WIDTH / 2) / (WIDTH / 2)) ** 2 + ((y - HEIGHT / 2) / (HEIGHT / 2)) ** 2)
    return np.clip((radius - 0.2) / 0.8, 0, 1) ** 1.7


VIGNETTE = _make_vignette()


def _load_caption_timeline(audio_path: Path, duration: float, segment_count: int) -> list[dict]:
    """Load exact caption timings if available; otherwise estimate timings."""
    timeline_path = audio_path.parent / "caption_timeline.json"
    if timeline_path.exists():
        data = json.loads(timeline_path.read_text(encoding="utf-8"))
        return [
            {"start": float(item["start"]), "end": float(item["end"]), "text": str(item["text"])}
            for item in data
        ]

    # Fallback for user-generated trailers without a caption_timeline.json file.
    # It still renders motion, but captions are generic because no exact line
    # timings are available.
    timeline = []
    for index in range(segment_count):
        start = duration * index / segment_count
        end = duration * (index + 1) / segment_count
        timeline.append({"start": start, "end": end, "text": DEFAULT_LABELS[index % len(DEFAULT_LABELS)]})
    return timeline


def _image_for_segment(images: list[Path], segment_index: int, segment_count: int) -> Path:
    """Map voice segments to scene images.

    For the included sample there are 8 voice segments and 6 images, so the
    warning and chase images are used twice to match the narration beats.
    """
    if len(images) >= 6 and segment_count == 8:
        mapping = [0, 1, 2, 2, 3, 3, 4, 5]
        return images[min(mapping[segment_index], len(images) - 1)]
    image_index = round(segment_index * (len(images) - 1) / max(1, segment_count - 1))
    return images[image_index]


def _motion_crop(background: np.ndarray, segment: int, progress: float, frame_no: int, fps: int) -> np.ndarray:
    # Jump-cut style camera movement every 1.25 seconds.
    shot_length = max(1, int(fps * 1.25))
    shot = int(frame_no / shot_length)
    local = (frame_no % shot_length) / max(1, shot_length - 1)
    ease = local * local * (3 - 2 * local)

    base_zoom = [1.10, 1.12, 1.13, 1.18, 1.14, 1.20, 1.13, 1.03][segment % 8]
    zoom = base_zoom + 0.12 * ease + 0.035 * (shot % 2)
    if segment % 8 in [4, 5]:
        zoom += 0.05 * math.sin(frame_no * 0.12)

    resized_width, resized_height = int(WIDTH * zoom), int(HEIGHT * zoom)
    resized = cv2.resize(background, (resized_width, resized_height), interpolation=cv2.INTER_CUBIC)

    anchors = [
        [(0.15, 0.52), (0.75, 0.45), (0.55, 0.58), (0.30, 0.40)],
        [(0.50, 0.60), (0.50, 0.30), (0.35, 0.45), (0.65, 0.42)],
        [(0.30, 0.38), (0.68, 0.56), (0.50, 0.48), (0.40, 0.60)],
        [(0.38, 0.44), (0.62, 0.52), (0.52, 0.34), (0.32, 0.55)],
        [(0.20, 0.50), (0.80, 0.50), (0.45, 0.37), (0.62, 0.62)],
        [(0.82, 0.54), (0.22, 0.48), (0.50, 0.70), (0.38, 0.34)],
        [(0.62, 0.62), (0.42, 0.34), (0.50, 0.50), (0.70, 0.40)],
        [(0.50, 0.50), (0.50, 0.50), (0.50, 0.50), (0.50, 0.50)],
    ][segment % 8]

    start = anchors[shot % len(anchors)]
    end = anchors[(shot + 1) % len(anchors)]
    anchor_x = start[0] + (end[0] - start[0]) * ease
    anchor_y = start[1] + (end[1] - start[1]) * ease

    max_x = resized_width - WIDTH
    max_y = resized_height - HEIGHT
    shake_amp = [1, 2, 4, 5, 13, 10, 5, 1][segment % 8]
    jitter_x = int(shake_amp * math.sin(frame_no * 0.72) + shake_amp * 0.5 * math.sin(frame_no * 1.9))
    jitter_y = int(shake_amp * 0.5 * math.cos(frame_no * 0.86))

    crop_x = max(0, min(max_x, int(max_x * anchor_x) + jitter_x))
    crop_y = max(0, min(max_y, int(max_y * anchor_y) + jitter_y))
    frame = resized[crop_y : crop_y + HEIGHT, crop_x : crop_x + WIDTH].copy()

    # Slight perspective sway to avoid a flat slideshow feel.
    if segment % 8 != 7:
        amp = [1.5, 2, 3, 3, 5, 4, 3, 1][segment % 8]
        yy, xx = np.indices((HEIGHT, WIDTH), dtype=np.float32)
        map_x = xx + amp * np.sin((yy / 80) + frame_no * 0.06)
        map_y = yy + amp * 0.55 * np.sin((xx / 110) + frame_no * 0.05)
        frame = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return frame


def _grade(frame: np.ndarray, segment: int) -> np.ndarray:
    arr = frame.astype(np.float32)
    if segment % 8 in [2, 3]:
        arr[:, :, 0] *= 1.18
        arr[:, :, 1] *= 0.85
    elif segment % 8 in [4, 5]:
        arr[:, :, 2] *= 1.2
        arr[:, :, 1] *= 0.98
    else:
        arr[:, :, 2] *= 1.08
        arr[:, :, 1] *= 1.03
    arr *= 1 - 0.43 * VIGNETTE[..., None]
    return np.clip(arr, 0, 255).astype(np.uint8)


def _draw_caption(frame: np.ndarray, text: str, alpha: float = 1.0) -> np.ndarray:
    if not text or alpha <= 0:
        return frame

    lines = textwrap.wrap(text, width=48)
    if len(lines) > 2:
        lines = [" ".join(lines[:-1]), lines[-1]]

    image = Image.fromarray(frame)
    draw = ImageDraw.Draw(image, "RGBA")
    line_height = 40
    total_height = line_height * len(lines) + 20
    y = HEIGHT - LETTERBOX - total_height - 18
    max_width = max(_text_size(line, FONT_CAPTION)[0] for line in lines)
    x = (WIDTH - max_width) // 2

    draw.rounded_rectangle(
        (x - 24, y - 12, x + max_width + 24, y + total_height),
        radius=16,
        fill=(0, 0, 0, int(178 * alpha)),
        outline=(0, 220, 255, int(80 * alpha)),
        width=1,
    )
    for index, line in enumerate(lines):
        line_width, _ = _text_size(line, FONT_CAPTION)
        draw.text(
            ((WIDTH - line_width) // 2, y + index * line_height),
            line,
            font=FONT_CAPTION,
            fill=(255, 255, 255, int(255 * alpha)),
            stroke_width=2,
            stroke_fill=(0, 0, 0, int(240 * alpha)),
        )
    return np.array(image)


def _hud(frame: np.ndarray, segment: int, progress: float) -> np.ndarray:
    frame[:LETTERBOX] = 0
    frame[HEIGHT - LETTERBOX :] = 0
    cv2.line(frame, (40, LETTERBOX + 8), (WIDTH - 40, LETTERBOX + 8), (0, 210, 255), 1)
    cv2.line(frame, (40, HEIGHT - LETTERBOX - 8), (WIDTH - 40, HEIGHT - LETTERBOX - 8), (0, 210, 255), 1)

    if segment % 8 != 7:
        scan_y = int(LETTERBOX + 8 + progress * (HEIGHT - 2 * LETTERBOX - 16))
        cv2.line(frame, (0, scan_y), (WIDTH, scan_y), (0, 255, 255), 2)

    label = DEFAULT_LABELS[segment % len(DEFAULT_LABELS)]
    image = Image.fromarray(frame)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((55, 18, 385, 50), radius=8, fill=(0, 0, 0, 130), outline=(0, 220, 255, 110), width=1)
    draw.text((70, 23), label, font=FONT_SMALL, fill=(210, 245, 255, 235))
    return np.array(image)


def _effect(frame: np.ndarray, segment: int, progress: float, frame_no: int, rng: random.Random) -> np.ndarray:
    scene = segment % 8

    if scene == 0:
        # Flying city vehicles.
        vehicle_rng = random.Random(44)
        vehicles = [
            (vehicle_rng.randrange(-WIDTH, WIDTH), vehicle_rng.randrange(90, 350), vehicle_rng.uniform(2, 8), vehicle_rng.choice([(0, 230, 255), (255, 60, 160), (255, 210, 60)]))
            for _ in range(70)
        ]
        for idx, (x0, y, speed, color) in enumerate(vehicles):
            x = int((x0 + frame_no * speed + idx * 20) % (WIDTH + 240) - 120)
            yy = int(y + 12 * math.sin(frame_no * 0.04 + idx))
            cv2.line(frame, (x - 42, yy), (x + 42, yy), color, 3)
            cv2.circle(frame, (x + 45, yy), 3, (255, 255, 255), -1)
            cv2.line(frame, (x - 125, yy), (x - 50, yy), color, 1)
        for i in range(12):
            x = int((i * 140 + frame_no * 2.4) % WIDTH)
            cv2.line(frame, (x, LETTERBOX), (x + 180, HEIGHT - LETTERBOX), (0, 170, 255), 1)

    elif scene == 1:
        # Animated AI core rings and binary rain.
        cx, cy = WIDTH // 2, HEIGHT // 2
        pulse = 0.5 + 0.5 * math.sin(frame_no * 0.22)
        for radius in [60, 110, 170, 240, 320]:
            cv2.ellipse(frame, (cx, cy), (int(radius * (1 + 0.1 * pulse)), int(radius * 0.52)), frame_no * (1 + radius / 90), 0, 340, (0, 220, 255), 2)
            cv2.ellipse(frame, (cx, cy), (int(radius * 1.15), int(radius * 0.62)), -frame_no * (0.8 + radius / 140), 20, 250, (180, 60, 255), 1)
        for i in range(50):
            x = 45 + (i % 8) * 155
            y = LETTERBOX + 25 + ((i * 35 + frame_no * 9) % (HEIGHT - 2 * LETTERBOX - 60))
            text = "".join(rng.choice("01") for _ in range(18))
            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 180 + rng.randrange(60), 255), 1, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy), int(48 + 28 * pulse), (120, 245, 255), -1)

    elif scene in [2, 3]:
        # Countdown and glitch alarm.
        if frame_no % 9 < 3:
            for _ in range(12):
                y = rng.randrange(LETTERBOX, HEIGHT - LETTERBOX - 6)
                h = rng.randrange(2, 12)
                shift = rng.randrange(-70, 70)
                frame[y : y + h] = np.roll(frame[y : y + h], shift, axis=1)
        pulse = 0.5 + 0.5 * math.sin(frame_no * 0.55)
        cv2.rectangle(frame, (26, LETTERBOX + 17), (WIDTH - 26, HEIGHT - LETTERBOX - 17), (0, 0, int(150 + 105 * pulse)), 3)
        timer_seconds = max(0, int((1 - progress) * (48 if scene == 2 else 12) * 3600))
        hh = timer_seconds // 3600
        mm = (timer_seconds % 3600) // 60
        ss = timer_seconds % 60
        timer = f"{hh:02d}:{mm:02d}:{ss:02d}"
        image = Image.fromarray(frame)
        draw = ImageDraw.Draw(image, "RGBA")
        timer_width, timer_height = _text_size(timer, FONT_TIMER)
        draw.rounded_rectangle(((WIDTH - timer_width) // 2 - 30, 105, (WIDTH + timer_width) // 2 + 30, 105 + timer_height + 34), radius=14, fill=(120, 0, 0, 135), outline=(255, 40, 40, 230), width=2)
        draw.text(((WIDTH - timer_width) // 2, 122), timer, font=FONT_TIMER, fill=(255, 68, 68, 255), stroke_width=3, stroke_fill=(0, 0, 0, 245))
        message = "TARGET: MAYA VOSS" if scene == 2 else "ELENA VOSS // OVERRIDE ACCESS"
        draw.text((82, 112), message, font=FONT_SMALL, fill=(255, 190, 190, 235), stroke_width=1, stroke_fill=(0, 0, 0, 220))
        frame = np.array(image)

    elif scene in [4, 5]:
        # Rain, searchlights, drones, speed streaks.
        overlay = frame.copy()
        rain_rng = random.Random(44)
        rain = [(rain_rng.randrange(-180, WIDTH + 180), rain_rng.randrange(-HEIGHT, HEIGHT), rain_rng.uniform(18, 32), rain_rng.uniform(-7, 2)) for _ in range(760)]
        for x0, y0, speed, drift in rain:
            x = int((x0 + drift * frame_no) % (WIDTH + 240) - 120)
            y = int((y0 + speed * frame_no) % (HEIGHT + 220) - 110)
            cv2.line(overlay, (x, y), (x - 18, y + 42), (180, 225, 255), 1)
        frame = cv2.addWeighted(overlay, 0.56, frame, 0.44, 0)
        for i in range(4):
            bx = int((i * 340 + 170 + 90 * math.sin(frame_no * 0.08 + i)) % WIDTH)
            top = (bx, LETTERBOX + 18)
            x1 = int(bx - 190 + 130 * math.sin(frame_no * 0.045 + i))
            points = np.array([top, (x1, HEIGHT - LETTERBOX - 15), (x1 + 310, HEIGHT - LETTERBOX - 15)], np.int32)
            light = np.zeros_like(frame)
            cv2.fillPoly(light, [points], (100, 180, 255))
            frame = cv2.addWeighted(light, 0.12, frame, 0.88, 0)
            cv2.circle(frame, top, 7, (220, 250, 255), -1)
        for i in range(8):
            x = int((WIDTH + 150 - (frame_no * (5 + i * 0.8) + i * 180)) % (WIDTH + 300) - 150)
            y = int(110 + i * 34 + 22 * math.sin(frame_no * 0.09 + i))
            cv2.line(frame, (x - 28, y), (x + 28, y), (3, 5, 8), 6)
            cv2.circle(frame, (x, y), 9, (4, 5, 9), -1)
            cv2.circle(frame, (x, y + 2), 3, (255, 30, 30), -1)
        for _ in range(35):
            y = rng.randrange(LETTERBOX + 35, HEIGHT - LETTERBOX - 35)
            x = rng.randrange(0, WIDTH)
            cv2.line(frame, (x, y), (x + rng.randrange(80, 210), y + rng.randrange(-12, 12)), (0, 190, 255), 1)

    elif scene == 6:
        # Final energy and upload bar.
        cx, cy = WIDTH // 2, HEIGHT // 2
        for radius in range(70, 700, 70):
            rr = int((radius + frame_no * 5) % 700)
            if rr > 40:
                cv2.circle(frame, (cx, cy), rr, (0, 220, 255), 1)
        for i in range(10):
            angle = frame_no * 0.06 + i * 0.7
            x1 = int(cx + math.cos(angle) * 70)
            y1 = int(cy + math.sin(angle) * 45)
            x2 = int(cx + math.cos(angle + 0.6) * 430)
            y2 = int(cy + math.sin(angle + 0.6) * 250)
            points = []
            for t in np.linspace(0, 1, 8):
                points.append((int(x1 + (x2 - x1) * t + rng.randrange(-16, 17)), int(y1 + (y2 - y1) * t + rng.randrange(-16, 17))))
            cv2.polylines(frame, [np.array(points, np.int32)], False, (130, 245, 255), 2)
        image = Image.fromarray(frame)
        draw = ImageDraw.Draw(image, "RGBA")
        x0, y0, x1, y1 = 180, HEIGHT - LETTERBOX - 115, WIDTH - 180, HEIGHT - LETTERBOX - 84
        draw.rounded_rectangle((x0, y0, x1, y1), radius=9, fill=(0, 0, 0, 170), outline=(0, 230, 255, 180), width=2)
        draw.rounded_rectangle((x0 + 5, y0 + 5, int(x0 + 5 + (x1 - x0 - 10) * progress), y1 - 5), radius=6, fill=(0, 230, 255, 190))
        draw.text((x0, y0 - 38), f"UPLOADING TRUTH // {int(progress * 100):02d}%", font=FONT_SMALL, fill=(220, 245, 255, 240), stroke_width=1, stroke_fill=(0, 0, 0, 240))
        frame = np.array(image)

    elif scene == 7:
        # Title reveal.
        frame = (frame.astype(np.float32) * 0.35).astype(np.uint8)
        star_rng = random.Random(44)
        stars = [(star_rng.randrange(WIDTH), star_rng.randrange(HEIGHT), star_rng.uniform(0.5, 1.8)) for _ in range(330)]
        for x, y, scale in stars:
            twinkle = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(frame_no * 0.08 + scale))
            cv2.circle(frame, (x, y), max(1, int(scale)), (int(130 * twinkle), int(220 * twinkle), 255), -1)
        alpha = min(1, max(0, (progress - 0.05) / 0.24))
        title = "SHADOWS OF TOMORROW"
        tagline = "CAN YOU OUTRUN THE FUTURE?"
        image = Image.fromarray(frame)
        draw = ImageDraw.Draw(image, "RGBA")
        title_width, _ = _text_size(title, FONT_BIG)
        x = (WIDTH - title_width) // 2
        y = 250
        for offset, opacity in [(14, 45), (8, 80), (4, 120)]:
            draw.text((x - offset, y), title, font=FONT_BIG, fill=(0, 220, 255, int(opacity * alpha)), stroke_width=1)
            draw.text((x + offset, y), title, font=FONT_BIG, fill=(160, 60, 255, int(opacity * alpha)), stroke_width=1)
        draw.text((x, y), title, font=FONT_BIG, fill=(240, 250, 255, int(255 * alpha)), stroke_width=3, stroke_fill=(0, 0, 0, int(230 * alpha)))
        tagline_width, _ = _text_size(tagline, FONT_MID)
        draw.text(((WIDTH - tagline_width) // 2, 370), tagline, font=FONT_MID, fill=(0, 230, 255, int(245 * alpha)), stroke_width=2, stroke_fill=(0, 0, 0, int(220 * alpha)))
        frame = np.array(image)

    # Dust/particle layer.
    if scene in [1, 6, 7]:
        for i in range(85):
            x = int((i * 79 + frame_no * (1.5 + i % 5)) % WIDTH)
            y = int((i * 137 + frame_no * (0.8 + i % 3)) % HEIGHT)
            cv2.circle(frame, (x, y), 1, (0, 200, 255), -1)
    return frame


def _transition(frame: np.ndarray, segment: int, frame_no: int, fps: int, rng: random.Random) -> np.ndarray:
    if segment > 0 and frame_no < int(0.18 * fps):
        fade = 1 - frame_no / max(1, int(0.18 * fps))
        frame = np.clip(frame * (1 - 0.62 * fade) + 255 * (0.62 * fade), 0, 255).astype(np.uint8)
        for _ in range(7):
            y = rng.randrange(LETTERBOX, HEIGHT - LETTERBOX - 8)
            h = rng.randrange(2, 16)
            shift = rng.randrange(-90, 90)
            frame[y : y + h] = np.roll(frame[y : y + h], shift, axis=1)
    return frame


def _render_frame(background: np.ndarray, segment: int, progress: float, frame_no: int, fps: int, caption_text: str | None, caption_alpha: float) -> np.ndarray:
    rng = random.Random(segment * 100000 + frame_no)
    frame = _motion_crop(background, segment, progress, frame_no, fps)
    frame = _effect(frame, segment, progress, frame_no, rng)
    frame = _grade(frame, segment)
    frame = _transition(frame, segment, frame_no, fps, rng)
    frame = _hud(frame, segment, progress)
    if caption_text:
        frame = _draw_caption(frame, caption_text, caption_alpha)
    return frame


def render_motion_trailer(
    image_paths: Iterable[str | Path],
    audio_path: str | Path,
    output_path: str | Path,
    fps: int = 30,
    crf: int = 22,
) -> Path:
    """Render a cinematic MP4 from scene images and narration audio.

    If `caption_timeline.json` exists beside `audio_path`, its exact timings are
    used for full captions. Otherwise, captions are estimated.
    """
    images = [Path(path) for path in image_paths]
    if not images:
        raise ValueError("At least one scene image is required.")

    audio = Path(audio_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    audio_clip = AudioFileClip(str(audio))
    duration = float(audio_clip.duration)
    audio_clip.close()

    timeline = _load_caption_timeline(audio, duration, max(len(images), 6))
    segment_count = len(timeline)
    backgrounds = [_fit_image(_image_for_segment(images, index, segment_count)) for index in range(segment_count)]

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    silent = output.with_name(output.stem + "_silent.mp4")
    render_cmd = [
        ffmpeg,
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-s",
        f"{WIDTH}x{HEIGHT}",
        "-pix_fmt",
        "rgb24",
        "-r",
        str(fps),
        "-i",
        "-",
        "-an",
        "-vcodec",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "medium",
        "-crf",
        str(crf),
        str(silent),
    ]

    proc = subprocess.Popen(render_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    assert proc.stdin is not None
    try:
        for index, item in enumerate(timeline):
            segment = index % 8
            start = float(item["start"])
            end = float(item["end"])
            text = str(item["text"])
            duration_seconds = max(0.1, end - start)
            frames = max(1, round(duration_seconds * fps))
            background = backgrounds[index]

            for frame_no in range(frames):
                progress = frame_no / max(1, frames - 1)
                caption_alpha = min(1, max(0, progress / 0.08)) * min(1, max(0, (1 - progress) / 0.07))
                frame = _render_frame(background, segment, progress, frame_no, fps, text, caption_alpha)
                proc.stdin.write(frame.tobytes())

            # Render pause between voice lines, so future captions do not drift.
            if index < len(timeline) - 1:
                gap = max(0.0, float(timeline[index + 1]["start"]) - end)
                gap_frames = max(0, round(gap * fps))
                next_segment = (index + 1) % 8
                next_background = backgrounds[index + 1]
                for gap_frame in range(gap_frames):
                    gap_progress = gap_frame / max(1, gap_frames - 1)
                    frame = _render_frame(next_background, next_segment, 0.0, gap_frame, fps, None, 0.0)
                    proc.stdin.write(frame.tobytes())
    finally:
        proc.stdin.close()
        return_code = proc.wait()
        if return_code:
            raise RuntimeError("FFmpeg failed while rendering the motion trailer.")

    mux_cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(silent),
        "-i",
        str(audio),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(output),
    ]
    subprocess.run(mux_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        silent.unlink()
    except OSError:
        pass
    return output
