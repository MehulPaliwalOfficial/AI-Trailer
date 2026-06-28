# AI Movie Trailer Generator

A submission-ready Generative AI project that converts a **movie title + genre + user idea** into a cinematic trailer package:

1. Story generation  
2. Trailer script generation  
3. Narration extraction  
4. AI image prompt generation  
5. Voice-over generation  
6. Final MP4 trailer assembly

The project follows the prompt document and presentation workflow supplied for **“Build an AI Movie Trailer Generator using Generative AI.”**

---

## Project Highlights

- **Frontend:** Streamlit web app
- **Backend:** Python pipeline
- **LLM:** Google Gemini API when configured
- **Fallback Mode:** Runs without API keys for demo/evaluation, uses the user's idea instead of generating the same story every time, and creates procedural concept visuals instead of blank cards
- **TTS:** Edge-TTS voice-over support
- **Video:** Motion-style MP4 assembly with Ken Burns zoom/pan effects, scan-line sweeps, vignettes, transition flashes, and title overlays
- **Sample Output Included:** A completed animated-style trailer for **“Shadows of Tomorrow”**

---

## Folder Structure

```text
AI_Movie_Trailer_Generator/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── app.py              # Streamlit UI
│   ├── cli.py              # Command-line runner
│   ├── pipeline.py         # End-to-end workflow
│   ├── prompts.py          # Prompt templates
│   ├── llm.py              # Gemini integration
│   ├── fallback.py         # Offline demo generator
│   └── media.py            # Voice, scene cards, video assembly
├── prompts/
│   └── prompt_document.md  # Final prompt document
├── docs/
│   ├── project_report.md
│   ├── architecture.md
│   └── submission_checklist.md
└── sample_outputs/
    ├── story.md
    ├── trailer_script.md
    ├── narration.txt
    ├── image_prompts.md
    ├── trailer_voice.mp3
    ├── final_movie_trailer.mp4
    └── assets/
        ├── scene_01.png
        ├── scene_02.png
        ├── scene_03.png
        ├── scene_04.png
        ├── scene_05.png
        └── title_card.png
```

---

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Optional: Configure Gemini API

The app works in offline fallback mode without an API key. To use Gemini:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
GEMINI_API_KEY=your_api_key_here
# Optional, use this if your account does not support the default model:
GEMINI_MODEL=gemini-2.0-flash
```

After adding the key, run the app or CLI again. If Gemini is being used, the output will show:

```text
Provider: Google Gemini
```

You can also set the key directly in your terminal:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 3. Run the Streamlit App

```bash
streamlit run src/app.py
```

Open the local URL shown in the terminal. Enter a movie title, genre, and your idea, then click **Generate Trailer**.

### 4. Run from Command Line

Text-only pipeline:

```bash
python -m src.cli --title "Shadows of Tomorrow" --genre "Sci-Fi Thriller" --idea "A scientist discovers that a predictive AI is secretly controlling the future."
```

Full media pipeline:

```bash
python -m src.cli --title "Shadows of Tomorrow" --genre "Sci-Fi Thriller" --idea "A scientist must save her daughter before a countdown ends." --media
```

Generated files are saved inside the `outputs/` folder.

---

## Sample Trailer Included

A ready-made sample is included:

- Movie: **Shadows of Tomorrow**
- Genre: **Sci-Fi Thriller**
- Video: `sample_outputs/final_movie_trailer.mp4`
- Motion effects included: synced full captions, jump-cut zooms, camera pans, chase-scene shake, rain, drones, searchlights, countdown UI, glitch transitions, and cinematic letterbox
- Voice-over: `sample_outputs/trailer_voice.mp3`
- Scene images: `sample_outputs/assets/`
- Synced captions: `sample_outputs/captions.srt` and `sample_outputs/caption_timeline.json`

This sample can be used directly during project submission or demonstration.

---

## Workflow

```text
Movie Title + Genre + User Idea
        ↓
Story Generation
        ↓
Trailer Script Generation
        ↓
Narration Extraction
        ↓
Image Prompt Generation
        ↓
AI Voice Generation
        ↓
Scene Image Creation
        ↓
Video Assembly
        ↓
Final Movie Trailer MP4
```

---

## Notes for Submission

Before submitting, update these placeholders if required:

- Presenter name
- College / department
- Roll number / registration number
- Course / subject name

The main files to submit are:

1. `AI_Movie_Trailer_Generator_Submission.zip`
2. `docs/project_report.md`
3. `sample_outputs/final_movie_trailer.mp4`
4. Existing presentation file, if your instructor requires PPT submission

---

## Future Enhancements

- Add direct DALL·E / Stable Diffusion image API integration
- Add background music generation
- Add subtitle overlays
- Export trailer in multiple aspect ratios
- Add user login and project history
- Deploy on Streamlit Cloud or Render
