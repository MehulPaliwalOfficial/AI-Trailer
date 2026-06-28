"""Media helpers for scene visuals, AI voice generation, and video assembly."""
from __future__ import annotations

import asyncio
import math
import random
import textwrap
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
        "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _extract_scene_prompts(image_prompts_md: str) -> list[str]:
    prompts: list[str] = []
    current: list[str] = []
    for line in image_prompts_md.splitlines():
        if line.startswith("## Scene"):
            if current:
                prompts.append(" ".join(current).strip())
                current = []
        elif line.strip() and not line.startswith("#"):
            current.append(line.strip())
    if current:
        prompts.append(" ".join(current).strip())
    return prompts or ["Cinematic movie trailer scene with dramatic lighting."]


def _theme(prompt: str, title: str) -> str:
    text = f"{prompt} {title}".lower()
    if any(word in text for word in ["dragon", "kingdom", "magic", "castle", "wizard", "fantasy", "egg", "myth"]):
        return "fantasy"
    if any(word in text for word in ["love", "romance", "railway", "station", "letter", "café", "cafe", "rain-washed"]):
        return "romance"
    if any(word in text for word in ["horror", "ghost", "haunted", "curse", "nightmare", "demon", "abandoned"]):
        return "horror"
    if any(word in text for word in ["detective", "crime", "murder", "evidence", "noir", "case", "interrogation"]):
        return "crime"
    if any(word in text for word in ["action", "explosion", "chase", "operative", "helicopter", "war", "mission"]):
        return "action"
    if any(word in text for word in ["ai", "future", "sci", "neon", "hologram", "drone", "cyber", "quantum", "robot"]):
        return "sci-fi"
    return "cinematic"


def _gradient(width: int, height: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        for x in range(width):
            pixels[x, y] = (r, g, b)
    return image


def _stars(draw: ImageDraw.ImageDraw, rng: random.Random, count: int = 120) -> None:
    for _ in range(count):
        x = rng.randint(0, 1280)
        y = rng.randint(20, 430)
        radius = rng.choice([1, 1, 1, 2])
        color = rng.choice([(255, 255, 255, 160), (120, 220, 255, 130), (255, 210, 120, 120)])
        draw.ellipse((x, y, x + radius, y + radius), fill=color)


def _draw_dragon(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float, color=(8, 10, 18, 235), glow=(255, 140, 40, 180)) -> None:
    # Body, neck, head, tail
    draw.ellipse((x, y, x + int(150 * scale), y + int(48 * scale)), fill=color)
    draw.line((x + int(115 * scale), y + int(18 * scale), x + int(190 * scale), y - int(34 * scale)), fill=color, width=max(3, int(13 * scale)))
    draw.ellipse((x + int(178 * scale), y - int(55 * scale), x + int(225 * scale), y - int(18 * scale)), fill=color)
    draw.line((x + int(5 * scale), y + int(25 * scale), x - int(92 * scale), y + int(74 * scale)), fill=color, width=max(2, int(9 * scale)))
    # Wings
    wing1 = [(x + int(58 * scale), y + int(8 * scale)), (x - int(40 * scale), y - int(110 * scale)), (x + int(112 * scale), y - int(50 * scale))]
    wing2 = [(x + int(88 * scale), y + int(8 * scale)), (x + int(210 * scale), y - int(118 * scale)), (x + int(132 * scale), y - int(44 * scale))]
    draw.polygon(wing1, fill=color)
    draw.polygon(wing2, fill=color)
    # Horns and fire/glow
    draw.polygon([(x + int(198 * scale), y - int(52 * scale)), (x + int(215 * scale), y - int(78 * scale)), (x + int(213 * scale), y - int(46 * scale))], fill=color)
    draw.polygon([(x + int(224 * scale), y - int(34 * scale)), (x + int(292 * scale), y - int(57 * scale)), (x + int(260 * scale), y - int(20 * scale))], fill=glow)


def _draw_fantasy(image: Image.Image, prompt: str, scene_number: int, rng: random.Random) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    _stars(draw, rng, 90)
    # Moon
    draw.ellipse((1010, 80, 1135, 205), fill=(255, 235, 175, 205))
    draw.ellipse((970, 60, 1102, 194), fill=(55, 28, 98, 170))
    # Mountains
    for i, base_x in enumerate(range(-180, 1280, 210)):
        peak = 250 + (i % 3) * 55
        draw.polygon([(base_x, 560), (base_x + 190, peak), (base_x + 390, 560)], fill=(16, 23, 54, 245))
        draw.polygon([(base_x + 190, peak), (base_x + 240, peak + 95), (base_x + 145, peak + 105)], fill=(185, 225, 255, 90))
    # Castle
    cx = 530
    draw.rectangle((cx, 330, cx + 220, 560), fill=(32, 28, 62, 245), outline=(125, 170, 255, 90), width=2)
    for tx in [cx - 35, cx + 45, cx + 180, cx + 255]:
        draw.rectangle((tx, 275, tx + 65, 560), fill=(24, 22, 52, 245), outline=(125, 170, 255, 80), width=2)
        draw.polygon([(tx - 8, 275), (tx + 32, 220), (tx + 73, 275)], fill=(80, 44, 128, 240))
    for wx in range(cx + 25, cx + 200, 45):
        draw.rectangle((wx, 385, wx + 16, 425), fill=(255, 190, 70, 180))
    # Glowing egg / magic foreground
    if "egg" in prompt.lower() or scene_number == 2:
        draw.ellipse((560, 505, 720, 690), fill=(70, 240, 255, 95), outline=(160, 255, 255, 230), width=5)
        draw.ellipse((595, 535, 685, 665), fill=(255, 210, 90, 220), outline=(255, 255, 180, 240), width=4)
        for r in [105, 145, 190]:
            draw.ellipse((640 - r, 600 - r, 640 + r, 600 + r), outline=(0, 220, 255, 70), width=3)
    # Dragons
    _draw_dragon(draw, 185, 255, 1.0, color=(4, 7, 16, 235), glow=(255, 110, 30, 190))
    _draw_dragon(draw, 810, 220, 0.78, color=(7, 7, 20, 225), glow=(80, 220, 255, 170))
    if "3" in prompt or "three" in prompt.lower() or "dragons" in prompt.lower():
        _draw_dragon(draw, 635, 145, 0.55, color=(8, 6, 16, 210), glow=(120, 255, 110, 160))
    # Magic streaks
    for _ in range(22):
        x = rng.randint(40, 1230)
        y = rng.randint(100, 610)
        draw.line((x, y, x + rng.randint(-70, 70), y + rng.randint(-30, 30)), fill=(0, 230, 255, 80), width=2)


def _draw_sci_fi(image: Image.Image, prompt: str, scene_number: int, rng: random.Random) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    _stars(draw, rng, 100)
    # Neon city skyline
    for i in range(22):
        x = i * 62 + rng.randint(-18, 18)
        h = rng.randint(150, 420)
        color = rng.choice([(8, 22, 55, 240), (14, 18, 70, 245), (22, 26, 80, 245)])
        draw.rectangle((x, 610 - h, x + rng.randint(35, 70), 610), fill=color, outline=(0, 200, 255, 70))
        for wy in range(610 - h + 18, 600, 42):
            draw.rectangle((x + 10, wy, x + 22, wy + 12), fill=(0, 220, 255, 100))
    # Grid and holograms
    for i in range(0, 1280, 80):
        draw.line((640, 720, i, 440), fill=(0, 180, 255, 50), width=1)
    for y in range(455, 720, 35):
        draw.line((0, y, 1280, y), fill=(0, 180, 255, 45), width=1)
    # AI core / hologram
    cx, cy = 650, 330
    for r in [70, 120, 175, 235]:
        draw.ellipse((cx - r, cy - int(r * 0.55), cx + r, cy + int(r * 0.55)), outline=(0, 225, 255, 145), width=3)
    draw.ellipse((cx - 42, cy - 42, cx + 42, cy + 42), fill=(95, 245, 255, 210))
    # Drones
    for _ in range(7):
        x = rng.randint(80, 1180)
        y = rng.randint(120, 360)
        draw.ellipse((x - 9, y - 7, x + 9, y + 7), fill=(5, 6, 10, 230))
        draw.line((x - 34, y, x + 34, y), fill=(5, 6, 10, 230), width=5)
        draw.ellipse((x - 3, y - 2, x + 3, y + 4), fill=(255, 20, 40, 220))


def _draw_romance(image: Image.Image, prompt: str, scene_number: int, rng: random.Random) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    # Railway station perspective
    draw.rectangle((0, 430, 1280, 720), fill=(22, 20, 32, 230))
    for x in [410, 870]:
        draw.line((x, 720, 620, 430), fill=(185, 185, 190, 210), width=7)
        draw.line((x + 80, 720, 660, 430), fill=(185, 185, 190, 210), width=7)
    for i in range(0, 12):
        y = 455 + i * 28
        draw.line((350 - i * 17, y, 930 + i * 17, y), fill=(120, 95, 90, 190), width=5)
    # Clock and station lights
    draw.ellipse((575, 105, 705, 235), fill=(245, 245, 220, 220), outline=(255, 210, 90, 230), width=5)
    draw.line((640, 170, 640, 125), fill=(10, 10, 20, 255), width=4)
    draw.line((640, 170, 675, 185), fill=(10, 10, 20, 255), width=4)
    for x in [170, 360, 920, 1110]:
        draw.ellipse((x - 38, 230, x + 38, 306), fill=(255, 210, 130, 80))
        draw.line((x, 0, x, 260), fill=(255, 210, 130, 120), width=3)
    # Couple silhouettes / umbrella
    draw.arc((520, 360, 760, 520), 180, 360, fill=(5, 7, 13, 245), width=18)
    draw.line((640, 435, 640, 610), fill=(5, 7, 13, 245), width=5)
    for x in [590, 690]:
        draw.ellipse((x - 23, 488, x + 23, 534), fill=(5, 7, 13, 245))
        draw.rectangle((x - 20, 532, x + 20, 630), fill=(5, 7, 13, 245))
    # Rain
    for _ in range(180):
        x = rng.randint(0, 1280)
        y = rng.randint(0, 720)
        draw.line((x, y, x - 10, y + 25), fill=(180, 220, 255, 70), width=1)


def _draw_horror(image: Image.Image, prompt: str, scene_number: int, rng: random.Random) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    _stars(draw, rng, 70)
    # Moon
    draw.ellipse((920, 70, 1070, 220), fill=(230, 235, 210, 190))
    # Haunted house
    draw.rectangle((430, 330, 820, 620), fill=(18, 16, 22, 250), outline=(105, 105, 130, 90), width=2)
    draw.polygon([(390, 330), (625, 210), (860, 330)], fill=(12, 12, 20, 250))
    for x in [455, 540, 700, 785]:
        draw.rectangle((x, 395, x + 35, 455), fill=(255, 190, 80, 120))
    draw.rectangle((600, 500, 660, 620), fill=(5, 5, 10, 255))
    # Trees
    for x in [70, 180, 1030, 1150, 1240]:
        draw.line((x, 720, x + rng.randint(-20, 20), 260), fill=(4, 5, 7, 255), width=12)
        for _ in range(7):
            y = rng.randint(250, 520)
            draw.line((x, y, x + rng.randint(-110, 110), y - rng.randint(15, 80)), fill=(4, 5, 7, 255), width=5)
    # Ghost/fog
    draw.ellipse((890, 360, 990, 510), fill=(230, 245, 255, 70))
    draw.ellipse((920, 395, 932, 410), fill=(0, 0, 0, 120))
    draw.ellipse((950, 395, 962, 410), fill=(0, 0, 0, 120))
    for i in range(9):
        y = 480 + i * 22
        draw.rectangle((0, y, 1280, y + 15), fill=(190, 210, 230, 25))


def _draw_action(image: Image.Image, prompt: str, scene_number: int, rng: random.Random) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    # Road perspective
    draw.polygon([(0, 720), (530, 405), (750, 405), (1280, 720)], fill=(28, 28, 35, 255))
    draw.line((640, 430, 640, 720), fill=(255, 225, 60, 220), width=7)
    for i in range(9):
        y = 450 + i * 33
        draw.line((640, y, 640, y + 16), fill=(255, 225, 60, 180), width=5)
    # Explosions
    for cx, cy, r in [(230, 390, 90), (1030, 420, 115)]:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 130, 30, 150))
        draw.ellipse((cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2), fill=(255, 235, 80, 200))
    # Cars
    for x, y, color in [(500, 545, (12, 18, 30, 255)), (735, 585, (30, 12, 18, 255))]:
        draw.rounded_rectangle((x, y, x + 190, y + 72), radius=18, fill=color, outline=(0, 220, 255, 120), width=2)
        draw.ellipse((x + 25, y + 55, x + 65, y + 95), fill=(2, 2, 3, 255))
        draw.ellipse((x + 125, y + 55, x + 165, y + 95), fill=(2, 2, 3, 255))
        draw.rectangle((x + 55, y + 12, x + 140, y + 38), fill=(120, 220, 255, 90))
    # Helicopter/drone
    draw.ellipse((590, 170, 700, 220), fill=(5, 7, 12, 240))
    draw.line((520, 160, 770, 160), fill=(5, 7, 12, 230), width=8)
    draw.line((695, 195, 780, 225), fill=(5, 7, 12, 230), width=7)


def _draw_crime(image: Image.Image, prompt: str, scene_number: int, rng: random.Random) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    # Noir city and evidence board
    for i in range(14):
        x = i * 95
        h = rng.randint(170, 430)
        draw.rectangle((x, 610 - h, x + 70, 610), fill=(10, 13, 22, 250), outline=(255, 210, 80, 35))
    board = (710, 170, 1140, 520)
    draw.rectangle(board, fill=(35, 24, 24, 220), outline=(255, 80, 80, 120), width=3)
    pins = [(780, 230), (950, 250), (1080, 330), (845, 430), (1010, 450)]
    for x, y in pins:
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 60, 60, 230))
    for i in range(len(pins) - 1):
        draw.line((pins[i], pins[i + 1]), fill=(255, 60, 60, 160), width=3)
    # Detective silhouette
    draw.ellipse((240, 315, 340, 415), fill=(5, 5, 8, 255))
    draw.polygon([(195, 315), (385, 315), (330, 270), (250, 270)], fill=(5, 5, 8, 255))
    draw.rectangle((220, 405, 360, 655), fill=(5, 5, 8, 255))
    draw.polygon([(220, 430), (120, 620), (210, 620)], fill=(5, 5, 8, 255))
    draw.line((380, 450, 500, 600), fill=(5, 5, 8, 255), width=20)
    for i in range(8):
        y = 500 + i * 18
        draw.rectangle((0, y, 1280, y + 8), fill=(180, 180, 190, 20))


def _draw_cinematic(image: Image.Image, prompt: str, scene_number: int, rng: random.Random) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    _stars(draw, rng, 110)
    # Generic dramatic landscape
    draw.ellipse((900, 80, 1040, 220), fill=(255, 220, 130, 140))
    for i, base_x in enumerate(range(-100, 1280, 180)):
        peak = rng.randint(280, 430)
        draw.polygon([(base_x, 640), (base_x + 160, peak), (base_x + 330, 640)], fill=(12, 18, 36, 245))
    draw.rectangle((520, 360, 760, 625), fill=(20, 20, 38, 230), outline=(0, 220, 255, 80), width=2)
    for r in [90, 150, 220]:
        draw.ellipse((640 - r, 480 - r, 640 + r, 480 + r), outline=(0, 220, 255, 55), width=3)


def _add_cinematic_overlays(image: Image.Image, prompt: str, scene_number: int, title: str, theme: str) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = image.size
    # Vignette
    vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for i in range(18):
        alpha = int(8 + i * 5)
        vd.rectangle((i * 10, i * 6, width - i * 10, height - i * 6), outline=(0, 0, 0, alpha), width=22)
    image.alpha_composite(vignette)
    # Letterbox bars
    draw.rectangle((0, 0, width, 70), fill=(0, 0, 0, 210))
    draw.rectangle((0, height - 72, width, height), fill=(0, 0, 0, 220))
    # HUD frame
    draw.rectangle((28, 86, width - 28, height - 90), outline=(0, 220, 255, 95), width=3)
    draw.line((60, 102, width - 60, 102), fill=(0, 220, 255, 90), width=1)
    draw.line((60, height - 108, width - 60, height - 108), fill=(0, 220, 255, 90), width=1)
    # Title labels: small, not covering the image
    title_font = _font(42, bold=True)
    scene_font = _font(26, bold=True)
    tag_font = _font(19, bold=True)
    draw.text((70, 24), title.upper(), font=scene_font, fill=(235, 248, 255, 245))
    draw.text((70, 118), f"SCENE {scene_number:02d}", font=title_font, fill=(0, 230, 255, 245), stroke_width=2, stroke_fill=(0, 0, 0, 180))
    draw.text((70, height - 52), f"{theme.upper()} CONCEPT VISUAL  •  AI MOVIE TRAILER GENERATOR", font=tag_font, fill=(185, 230, 245, 220))
    # Short scene hint only, never the full long prompt
    hint = " ".join(textwrap.wrap(prompt, width=70)[:1])
    if hint:
        draw.rounded_rectangle((390, height - 62, width - 68, height - 18), radius=12, fill=(0, 0, 0, 115), outline=(0, 220, 255, 50), width=1)
        draw.text((410, height - 50), hint[:105], font=_font(18), fill=(230, 235, 245, 210))


def create_scene_card(prompt: str, scene_number: int, output_path: str | Path, title: str) -> Path:
    """Create a visual fallback scene image from a prompt.

    This is used when no real image-generation API is configured. It does not
    claim to be Stable Diffusion/DALL-E output; it is procedural concept art so
    the generated trailer is not a blank slideshow.
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1280, 720
    seed_text = f"{title}|{scene_number}|{prompt}"
    rng = random.Random(sum((i + 1) * ord(ch) for i, ch in enumerate(seed_text)))
    theme = _theme(prompt, title)

    palettes = {
        "fantasy": ((18, 12, 48), (92, 45, 130)),
        "romance": ((20, 18, 48), (110, 48, 78)),
        "horror": ((4, 6, 10), (42, 35, 48)),
        "crime": ((8, 10, 18), (52, 38, 30)),
        "action": ((20, 18, 28), (100, 45, 20)),
        "sci-fi": ((4, 10, 35), (20, 35, 90)),
        "cinematic": ((8, 10, 30), (52, 38, 78)),
    }
    top, bottom = palettes.get(theme, palettes["cinematic"])
    image = _gradient(width, height, top, bottom).convert("RGBA")

    if theme == "fantasy":
        _draw_fantasy(image, prompt, scene_number, rng)
    elif theme == "romance":
        _draw_romance(image, prompt, scene_number, rng)
    elif theme == "horror":
        _draw_horror(image, prompt, scene_number, rng)
    elif theme == "crime":
        _draw_crime(image, prompt, scene_number, rng)
    elif theme == "action":
        _draw_action(image, prompt, scene_number, rng)
    elif theme == "sci-fi":
        _draw_sci_fi(image, prompt, scene_number, rng)
    else:
        _draw_cinematic(image, prompt, scene_number, rng)

    # Final cinematic glow/blur composite
    glow = image.filter(ImageFilter.GaussianBlur(10))
    image = Image.blend(glow, image, 0.78)
    _add_cinematic_overlays(image, prompt, scene_number, title, theme)

    image.convert("RGB").save(output, quality=95)
    return output


def create_scene_cards(image_prompts_md: str, output_dir: str | Path, title: str) -> list[Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    prompts = _extract_scene_prompts(image_prompts_md)
    paths = []
    for i, prompt in enumerate(prompts[:5], start=1):
        paths.append(create_scene_card(prompt, i, output / f"scene_{i:02d}.png", title))
    return paths


async def _edge_tts_async(text: str, output_path: Path, voice: str) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(str(output_path))


def generate_voice(text: str, output_path: str | Path, voice: str = "en-US-JennyNeural") -> Path:
    """Generate narration audio with Edge-TTS."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(_edge_tts_async(text, output, voice))
    return output


def assemble_video(
    image_paths: Iterable[str | Path],
    audio_path: str | Path,
    output_path: str | Path,
    fps: int = 24,
) -> Path:
    """Assemble scene images and narration into a cinematic motion MP4.

    The renderer adds visible animation effects: camera moves, punch-in cuts,
    rain, searchlights, moving drones/vehicles, AI HUD overlays, countdown UI,
    glitch transitions, subtitles, and a title reveal.
    """
    try:
        from .cinematic_renderer import render_motion_trailer
    except ImportError:  # pragma: no cover - supports running src files directly
        from cinematic_renderer import render_motion_trailer

    return render_motion_trailer(image_paths, audio_path, output_path, fps=fps)
