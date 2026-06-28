# Architecture – AI Movie Trailer Generator

## System Overview

The project uses a modular pipeline where each stage produces an output that becomes the input for the next stage. This technique is called **prompt chaining**.

```text
User Input
  ├── Movie Title
  ├── Genre
  └── User Idea / Plot / Characters / Mood
       ↓
Prompt 1: Story Generation
       ↓
Prompt 2: Trailer Script Generation
       ↓
Prompt 3: Narration Extraction
       ↓
Prompt 4: Image Prompt Generation
       ↓
Prompt 5: Voice Generation
       ↓
Prompt 6: Video Assembly
       ↓
Final Movie Trailer
```

## Components

### 1. User Interface

Implemented using Streamlit. It collects:

- Movie title
- Genre
- User idea / plot / characters / mood
- Optional media generation setting
- TTS voice selection

### 2. Prompt Engine

Defined in `src/prompts.py`. It stores reusable prompt templates for:

- Story creation
- Trailer script generation
- Narration extraction
- Image prompt generation

### 3. LLM Layer

Defined in `src/llm.py`. It uses Gemini if an API key is present:

- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`

If no API key is available, the system automatically switches to offline fallback mode.

### 4. Fallback Generator

Defined in `src/fallback.py`. It makes the project runnable without internet or API credentials. This is useful for demonstrations and classroom evaluation.

### 5. Media Layer

Defined in `src/media.py`. It handles:

- Scene-card generation using Pillow
- Voice-over generation using Edge-TTS
- Motion-style MP4 assembly using FFmpeg/ImageIO and MoviePy audio timing

### 6. Output Layer

The pipeline writes generated artifacts into an output directory:

- `story.md`
- `trailer_script.md`
- `narration.txt`
- `image_prompts.md`
- `trailer_voice.mp3`
- `final_movie_trailer.mp4`

## Data Flow

1. User enters title, genre, and an optional idea/plot/character/mood description.
2. Story prompt creates structured story.
3. Trailer prompt converts story to five trailer scenes.
4. Narration prompt extracts only voice-over lines.
5. Image prompt stage creates cinematic visual prompts.
6. TTS converts narration to audio.
7. Images and audio are combined into MP4.

## Design Benefits

- Modular and easy to understand
- API-ready but works without keys
- Clear prompt engineering examples
- Demonstrates real Generative AI workflow
- Suitable for demo, report, and practical submission
