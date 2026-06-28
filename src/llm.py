"""Gemini integration with safe offline fallback support.

The project uses Gemini when GEMINI_API_KEY or GOOGLE_API_KEY is available.
If Gemini is unavailable or a selected model is not supported, the pipeline
falls back to the offline demo generator.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Load API keys from a local .env file automatically.
# The real .env file is ignored by GitHub through .gitignore.
try:
    from dotenv import load_dotenv

    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")
    load_dotenv()
except Exception:
    pass


@dataclass
class LLMResult:
    text: str
    provider: str


class GeminiNotAvailable(RuntimeError):
    """Raised when Gemini cannot be used in the current environment."""


def _api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def _model_candidates(model_name: str | None = None) -> list[str]:
    """Return Gemini model candidates.

    Gemini 1.5 model availability differs by account/date. Newer accounts often
    need Gemini 2.x/2.5 model names, so the app tries multiple names.
    """
    candidates: list[str] = []
    env_model = os.getenv("GEMINI_MODEL")
    if model_name:
        candidates.append(model_name)
    if env_model:
        candidates.append(env_model)

    candidates.extend(
        [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
        ]
    )

    # Remove duplicates while preserving order.
    unique: list[str] = []
    for item in candidates:
        if item and item not in unique:
            unique.append(item)
    return unique


def gemini_available() -> bool:
    """Return True if the runtime appears to be configured for Gemini."""
    if not _api_key():
        return False
    try:
        from google import genai  # noqa: F401

        return True
    except Exception:
        pass
    try:
        import google.generativeai  # noqa: F401

        return True
    except Exception:
        return False


def _generate_with_google_genai(prompt: str, key: str, models: list[str]) -> LLMResult:
    """Use the current google-genai SDK."""
    from google import genai

    client = genai.Client(api_key=key)
    errors: list[str] = []
    for model in models:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            text = getattr(response, "text", "") or ""
            if text.strip():
                return LLMResult(text=text.strip(), provider=f"Google Gemini ({model})")
        except Exception as exc:
            errors.append(f"{model}: {exc}")
    raise GeminiNotAvailable("All Gemini models failed: " + " | ".join(errors[-3:]))


def _generate_with_legacy_google_generativeai(prompt: str, key: str, models: list[str]) -> LLMResult:
    """Use the deprecated google-generativeai SDK as a fallback."""
    import google.generativeai as genai

    genai.configure(api_key=key)
    errors: list[str] = []
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = getattr(response, "text", "") or ""
            if text.strip():
                return LLMResult(text=text.strip(), provider=f"Google Gemini ({model_name})")
        except Exception as exc:
            errors.append(f"{model_name}: {exc}")
    raise GeminiNotAvailable("All Gemini models failed: " + " | ".join(errors[-3:]))


def generate_text(prompt: str, model_name: str | None = None) -> LLMResult:
    """Generate text with Gemini.

    Raises GeminiNotAvailable if no API key/package/model is available. The
    caller catches this and uses fallback logic.
    """
    key = _api_key()
    if not key:
        raise GeminiNotAvailable("Set GEMINI_API_KEY or GOOGLE_API_KEY to use Gemini.")

    models = _model_candidates(model_name)

    # Prefer the new SDK.
    try:
        return _generate_with_google_genai(prompt, key, models)
    except ImportError:
        pass
    except Exception as new_sdk_error:
        # If the new SDK exists but fails, still try the legacy SDK before falling back.
        legacy_error_prefix = str(new_sdk_error)
    else:
        legacy_error_prefix = ""

    try:
        return _generate_with_legacy_google_generativeai(prompt, key, models)
    except ImportError as exc:
        raise GeminiNotAvailable(
            "Gemini SDK is not installed. Run: pip install -r requirements.txt"
        ) from exc
    except Exception as exc:
        raise GeminiNotAvailable(f"Gemini failed. {exc}") from exc
