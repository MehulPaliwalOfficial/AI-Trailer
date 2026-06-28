# Project Report: AI Movie Trailer Generator Using Generative AI

**Student Name:** ____________________  
**Roll Number:** ____________________  
**College / Department:** ____________________  
**Course / Subject:** ____________________  
**Date:** 28 June 2026

---

## 1. Abstract

The **AI Movie Trailer Generator** is a Generative AI based application that converts a simple movie idea into a complete trailer package. The user provides a movie title, genre, and optional idea/plot/characters/mood. The system then generates a story, creates a cinematic trailer script, extracts narration, prepares image generation prompts, converts narration into voice, and assembles a final trailer video.

This project demonstrates how multiple AI tools can be combined into a single creative workflow. It uses prompt engineering, large language models, text-to-speech, AI image generation concepts, and automated video assembly.

---

## 2. Introduction

Generative AI can create new text, images, audio, and video from natural language instructions. In traditional film production, trailer creation requires writers, designers, voice artists, and video editors. This project shows how the same workflow can be automated using AI-based tools.

The application is useful for students, content creators, marketers, and filmmakers who want to quickly prototype movie concepts and promotional trailer ideas.

---

## 3. Objectives

The main objectives of the project are:

1. To generate a creative movie story from title, genre, and the user's own idea.
2. To convert the story into a five-scene cinematic trailer script.
3. To extract a clean voice-over narration from the trailer script.
4. To generate detailed image prompts for trailer visuals.
5. To create AI voice narration using text-to-speech.
6. To assemble images and narration into a final MP4 trailer.
7. To demonstrate prompt chaining in a practical Generative AI application.

---

## 4. Tools and Technologies Used

| Category | Tool / Technology |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| LLM / Text Generation | Google Gemini API / Offline fallback |
| Prompt Engineering | Structured prompt templates |
| Text-to-Speech | Edge-TTS |
| Image Handling | Pillow |
| Video Assembly | MoviePy |
| Output Format | Markdown, MP3, PNG, MP4 |

---

## 5. System Architecture

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
Voice Generation
        ↓
Scene Image Creation
        ↓
Video Assembly
        ↓
Final Movie Trailer
```

The system is divided into independent modules. Each module performs one task and passes its output to the next module. This makes the application easy to maintain and improve.

---

## 6. Module Description

### 6.1 Story Generation Module

This module accepts the movie title, genre, and user idea. It generates a structured story containing summary, characters, setting, and central conflict.

### 6.2 Trailer Script Module

This module converts the story into five cinematic scenes. Each scene includes visual description and narration.

### 6.3 Narration Extraction Module

This module extracts only the voice-over lines from the trailer script. The result is used for text-to-speech conversion.

### 6.4 Image Prompt Module

This module creates detailed visual prompts for AI image generation models. Each prompt includes environment, lighting, camera angle, mood, and cinematic details.

### 6.5 Voice Generation Module

This module converts narration text into an MP3 voice-over file using Edge-TTS.

### 6.6 Video Assembly Module

This module combines scene images and narration audio into a final MP4 movie trailer using MoviePy.

---

## 7. Prompt Engineering

Prompt engineering is the most important part of this project. Clear prompts produce structured and useful outputs. The prompts are designed to guide the AI model step-by-step instead of asking for the final trailer in one request.

Example prompt stages:

1. Generate story
2. Generate trailer script
3. Extract narration
4. Generate image prompts
5. Convert narration to speech
6. Compile video

This approach improves output quality and makes debugging easier.

---

## 8. Sample Output

Sample movie used for demonstration:

- **Movie Title:** Shadows of Tomorrow
- **Genre:** Sci-Fi Thriller

Generated sample files:

- `sample_outputs/story.md`
- `sample_outputs/trailer_script.md`
- `sample_outputs/narration.txt`
- `sample_outputs/image_prompts.md`
- `sample_outputs/trailer_voice.mp3`
- `sample_outputs/final_movie_trailer.mp4`

The final trailer is approximately 42 seconds long and contains AI-generated cinematic scene images, a title card, synced full captions, voice-over narration, and motion effects such as jump-cut zooms, camera pans, rain, searchlights, drones, countdown UI, glitch transitions, and chase-scene shake.

---

## 9. Advantages

- Reduces time required to create trailer concepts.
- Demonstrates multiple AI tools in one workflow.
- Easy to customize for different movie genres.
- Can run with Gemini API or in offline fallback mode.
- Produces text, audio, image, and video outputs.

---

## 10. Limitations

- Real AI image generation requires an image model or external tool.
- Voice quality depends on the selected TTS service.
- Background music is not automatically generated in this version.
- LLM output quality depends on prompt clarity and model capability.

---

## 11. Future Scope

Future improvements can include:

- Direct Stable Diffusion or DALL·E API integration.
- Automatic background music generation.
- Subtitle overlay support.
- Multiple voice options.
- Web deployment.
- User accounts and trailer history.
- Export to YouTube Shorts / Instagram Reels formats.

---

## 12. Conclusion

The AI Movie Trailer Generator successfully demonstrates how Generative AI can automate a creative media production workflow. The project combines story generation, script writing, narration extraction, image prompting, text-to-speech, and video compilation. It is a practical example of prompt chaining and AI orchestration, showing how multiple AI technologies can work together to produce a complete multimedia output.
