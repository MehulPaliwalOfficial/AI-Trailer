"""Streamlit web app for the AI Movie Trailer Generator.

Run from the project folder:
    streamlit run src/app.py
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

try:
    from .pipeline import run_pipeline
except ImportError:  # pragma: no cover
    from pipeline import run_pipeline


st.set_page_config(page_title="AI Movie Trailer Generator", page_icon="🎬", layout="wide")
st.title("🎬 AI Movie Trailer Generator")
st.caption("From your idea to story, trailer script, narration, image prompts, voice, and video.")

with st.sidebar:
    st.header("Input")
    title = st.text_input("Movie Title", value="Shadows of Tomorrow")
    genre = st.text_input("Genre", value="Sci-Fi Thriller")
    idea = st.text_area(
        "Your Idea / Plot / Characters / Mood",
        value="A scientist discovers that a predictive AI is secretly controlling the future and must save her daughter before a countdown ends.",
        height=140,
        help="Write anything you want in the trailer: story idea, main character, villain, location, mood, twist, or ending.",
    )
    generate_media = st.checkbox("Generate fallback concept visuals + voice + MP4", value=False)
    voice = st.text_input("Edge-TTS Voice", value="en-US-JennyNeural")
    st.info("Set GEMINI_API_KEY or GOOGLE_API_KEY to use Gemini. Without quota/API access, the app uses idea-based offline fallback mode.")

if st.button("Generate Trailer", type="primary"):
    with st.spinner("Generating trailer pipeline..."):
        result = run_pipeline(
            title,
            genre,
            movie_idea=idea,
            output_dir="outputs",
            generate_media=generate_media,
            voice=voice,
        )

    st.success(f"Done! Provider: {result.provider}")
    st.write(f"Output folder: `{result.output_dir}`")

    tab_idea, tab_story, tab_script, tab_narration, tab_images, tab_media = st.tabs(
        ["Idea", "Story", "Trailer Script", "Narration", "Image Prompts", "Media"]
    )

    with tab_idea:
        st.subheader("User Idea")
        st.write(result.idea)
    with tab_story:
        st.markdown(result.story)
    with tab_script:
        st.markdown(result.trailer_script)
    with tab_narration:
        st.write(result.narration)
        st.download_button("Download narration.txt", result.narration, "narration.txt")
    with tab_images:
        st.markdown(result.image_prompts)
    with tab_media:
        if result.scene_images:
            cols = st.columns(min(3, len(result.scene_images)))
            for i, path in enumerate(result.scene_images):
                with cols[i % len(cols)]:
                    st.image(str(path), caption=Path(path).name)
        if result.voice_path and Path(result.voice_path).exists():
            st.audio(str(result.voice_path))
        if result.video_path and Path(result.video_path).exists():
            st.video(str(result.video_path))
        if not result.scene_images and not result.video_path:
            st.info("Enable media generation in the sidebar to create fallback concept visuals, narration audio, and MP4 video.")
else:
    st.markdown(
        """
        ### Workflow
        1. Enter a movie title, genre, and your own idea.  
        2. Gemini or the idea-based fallback creates a story.  
        3. The story becomes a 5-scene trailer script.  
        4. Narration is extracted for voice-over.  
        5. Image prompts are created for cinematic scene visuals.  
        6. Optional media mode generates fallback concept visuals, TTS voice, and MP4 video.

        ### Idea examples
        - "A ghost follows a school student who can see future accidents."  
        - "Two strangers fall in love during a time loop at a railway station."  
        - "A village boy discovers a dragon egg during a war between kingdoms."  
        - "A detective has 24 hours to solve a murder committed by his future self."
        """
    )
