"""End-to-end trailer generation pipeline."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

try:  # Allows both `python -m src.cli` and `streamlit run src/app.py`.
    from . import fallback
    from .llm import GeminiNotAvailable, generate_text
    from .media import assemble_video, create_scene_cards, generate_voice
    from .prompts import IMAGE_PROMPT, NARRATION_PROMPT, STORY_PROMPT, TRAILER_PROMPT
except ImportError:  # pragma: no cover
    import fallback
    from llm import GeminiNotAvailable, generate_text
    from media import assemble_video, create_scene_cards, generate_voice
    from prompts import IMAGE_PROMPT, NARRATION_PROMPT, STORY_PROMPT, TRAILER_PROMPT


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value or "movie-trailer"


@dataclass
class PipelineResult:
    title: str
    genre: str
    idea: str
    provider: str
    output_dir: Path
    story: str
    trailer_script: str
    narration: str
    image_prompts: str
    scene_images: list[Path]
    voice_path: Path | None = None
    video_path: Path | None = None


def _ai_or_fallback(prompt: str, fallback_text: str) -> tuple[str, str]:
    try:
        result = generate_text(prompt)
        if result.text:
            return result.text, result.provider
    except GeminiNotAvailable:
        pass
    except Exception as exc:
        print(f"Gemini failed, using fallback: {exc}")
    return fallback_text, "Offline fallback generator"


def run_pipeline(
    movie_title: str,
    genre: str,
    movie_idea: str = "",
    output_dir: str | Path = "outputs",
    generate_media: bool = False,
    voice: str = "en-US-JennyNeural",
) -> PipelineResult:
    """Run the full text pipeline and optionally create media files."""
    title = movie_title.strip() or "Shadows of Tomorrow"
    genre = genre.strip() or "Sci-Fi Thriller"
    idea = movie_idea.strip() or "A scientist discovers that a predictive AI is secretly controlling the future."
    out = Path(output_dir) / slugify(title)
    out.mkdir(parents=True, exist_ok=True)
    (out / "user_idea.txt").write_text(idea, encoding="utf-8")

    story_prompt = STORY_PROMPT.format(movie_title=title, genre=genre, idea=idea)
    story, provider = _ai_or_fallback(story_prompt, fallback.generate_story(title, genre, idea))
    (out / "story.md").write_text(story, encoding="utf-8")

    trailer_prompt = TRAILER_PROMPT.format(story=story, idea=idea)
    trailer_script, provider2 = _ai_or_fallback(trailer_prompt, fallback.generate_trailer_script(story, title, genre, idea))
    if provider2 != "Offline fallback generator":
        provider = provider2
    (out / "trailer_script.md").write_text(trailer_script, encoding="utf-8")

    narration_prompt = NARRATION_PROMPT.format(trailer_script=trailer_script)
    narration_fallback = fallback.extract_narration(trailer_script)
    narration, provider3 = _ai_or_fallback(narration_prompt, narration_fallback)
    if provider3 != "Offline fallback generator":
        provider = provider3
    (out / "narration.txt").write_text(narration, encoding="utf-8")

    image_prompt = IMAGE_PROMPT.format(trailer_script=trailer_script)
    image_prompts_fallback = fallback.generate_image_prompts(trailer_script)
    image_prompts, provider4 = _ai_or_fallback(image_prompt, image_prompts_fallback)
    if provider4 != "Offline fallback generator":
        provider = provider4
    (out / "image_prompts.md").write_text(image_prompts, encoding="utf-8")

    scene_images: list[Path] = []
    voice_path: Path | None = None
    video_path: Path | None = None
    if generate_media:
        scene_images = create_scene_cards(image_prompts, out / "assets", title)
        try:
            voice_path = generate_voice(narration, out / "trailer_voice.mp3", voice=voice)
            video_path = assemble_video(scene_images, voice_path, out / "final_movie_trailer.mp4")
        except Exception as exc:
            print(f"Media generation warning: {exc}")

    return PipelineResult(
        title=title,
        genre=genre,
        idea=idea,
        provider=provider,
        output_dir=out,
        story=story,
        trailer_script=trailer_script,
        narration=narration,
        image_prompts=image_prompts,
        scene_images=scene_images,
        voice_path=voice_path,
        video_path=video_path,
    )
