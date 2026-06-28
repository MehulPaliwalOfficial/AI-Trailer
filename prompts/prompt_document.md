# AI Movie Trailer Generator – Prompt Document

## Prompt 1: Story Generation
**Objective:** Generate a movie story based on user input.

**User Inputs:** Movie Title, Genre, User Idea / Plot / Characters / Mood

**Prompt:**
Create a compelling movie story based on the following details:

Movie Title: {movie_title}
Genre: {genre}
User Idea / Plot / Characters / Mood: {idea}

Generate:
1. Story Summary (200-300 words)
2. Main Characters
3. Setting
4. Central Conflict

The story should be creative, engaging, and suitable for a cinematic movie trailer. Use the user's idea as the main creative direction.

## Prompt 2: Trailer Script Generation
**Objective:** Convert the generated story into a cinematic trailer script.

**Prompt:**
Based on the story below, generate a cinematic movie trailer.

User Idea / Creative Direction:
{idea}

Requirements:
- Create 5 trailer scenes.
- For each scene provide:
  - Visual Description
  - Narration
- End with a dramatic movie-trailer style hook.
- Also provide the Background Music Mood.

Story:
{story}

## Prompt 3: Narration Extraction
**Objective:** Extract only the voice-over narration from the trailer script.

**Prompt:**
Extract only the narration lines from the movie trailer below.

Do not include:
- Scene numbers
- Visual descriptions
- Background music instructions

Return only the narration as a continuous movie trailer voice-over script.

Trailer:
{trailer_script}

## Prompt 4: Image Prompt Generation
**Objective:** Generate detailed prompts for AI image creation.

**Prompt:**
From the movie trailer below, extract the first 3 scenes.
For each scene, generate a highly detailed cinematic image generation prompt.

Include:
- Environment
- Lighting
- Camera Angle
- Mood
- Cinematic Details

The output should be suitable for AI image generation models.

Trailer:
{trailer_script}

## Prompt 5: Voice Generation
**Objective:** Convert narration into speech.

Model Used: Edge-TTS  
Voice: en-US-JennyNeural  
Output: trailer_voice.mp3

## Prompt 6: Video Generation
**Objective:** Create a movie trailer video.

Inputs:
- Scene Images
- AI Narration Audio

Processing:
1. Load generated images.
2. Create image clips.
3. Match image duration with narration duration.
4. Merge clips.
5. Add narration audio.
6. Export final MP4 trailer.

Output: final_movie_trailer.mp4
