"""Command-line interface for the AI Movie Trailer Generator."""
from __future__ import annotations

import argparse

try:
    from .pipeline import run_pipeline
except ImportError:  # pragma: no cover
    from pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an AI movie trailer package.")
    parser.add_argument("--title", default="Shadows of Tomorrow", help="Movie title")
    parser.add_argument("--genre", default="Sci-Fi Thriller", help="Movie genre")
    parser.add_argument(
        "--idea",
        default="A scientist discovers that a predictive AI is secretly controlling the future.",
        help="Optional user idea, plot, characters, mood, or twist for the trailer",
    )
    parser.add_argument("--out", default="outputs", help="Output directory")
    parser.add_argument("--media", action="store_true", help="Also generate scene cards, TTS voice, and MP4 video")
    parser.add_argument("--voice", default="en-US-JennyNeural", help="Edge-TTS voice name")
    args = parser.parse_args()

    result = run_pipeline(
        args.title,
        args.genre,
        movie_idea=args.idea,
        output_dir=args.out,
        generate_media=args.media,
        voice=args.voice,
    )
    print("\nAI Movie Trailer generated successfully!")
    print(f"Provider: {result.provider}")
    print(f"Output folder: {result.output_dir}")
    print("Files created: user_idea.txt, story.md, trailer_script.md, narration.txt, image_prompts.md")
    if result.video_path:
        print(f"Final trailer video: {result.video_path}")


if __name__ == "__main__":
    main()
