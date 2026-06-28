"""Prompt templates used by the AI Movie Trailer Generator."""

STORY_PROMPT = """
Create a compelling movie story based on the following details:

Movie Title: {movie_title}
Genre: {genre}
User Idea / Plot / Characters / Mood: {idea}

Generate:
1. Story Summary (200-300 words)
2. Main Characters
3. Setting
4. Central Conflict

Important:
- Use the user's idea as the main creative direction.
- If the idea includes characters, locations, mood, or a twist, include them.
- The story should be creative, engaging, and suitable for a cinematic movie trailer.
""".strip()

TRAILER_PROMPT = """
Based on the story below, generate a cinematic movie trailer.

User Idea / Creative Direction:
{idea}

Requirements:
- Create 5 trailer scenes.
- For each scene provide:
  - Visual Description
  - Narration
- Make the scenes match the movie title, genre, and user idea.
- End with a dramatic movie-trailer style hook.
- Also provide the Background Music Mood.

Story:
{story}
""".strip()

NARRATION_PROMPT = """
Extract only the narration lines from the movie trailer below.

Do not include:
- Scene numbers
- Visual descriptions
- Background music instructions

Return only the narration as a continuous movie trailer voice-over script.

Trailer:
{trailer_script}
""".strip()

IMAGE_PROMPT = """
From the movie trailer below, extract the first 5 scenes.

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
""".strip()
