"""Deterministic fallback generation for demos without API keys.

The fallback is not a replacement for Gemini, but it should still feel useful.
It now uses the movie title, genre, and optional user idea to create different
stories, scripts, narration, and image prompts when API quota is unavailable.
"""
from __future__ import annotations

import re
from textwrap import dedent


def _clean(value: str, default: str) -> str:
    return " ".join((value or "").strip().split()) or default


def _seed(text: str) -> int:
    return sum((i + 1) * ord(ch) for i, ch in enumerate(text))


def _pick(options: list[str], seed_text: str) -> str:
    return options[_seed(seed_text) % len(options)]


def _profile(genre: str) -> dict[str, str]:
    g = genre.lower()
    if any(word in g for word in ["horror", "ghost", "supernatural"]):
        return {
            "setting": "an isolated town where old legends return after sunset",
            "hero_role": "a fearless paranormal investigator",
            "ally_role": "a skeptical local journalist",
            "antagonist": "an ancient presence hidden inside the town's history",
            "threat": "a curse that turns memories into nightmares",
            "visual": "foggy streets, abandoned houses, candlelit rooms, and shadows moving by themselves",
            "music": "low horror drones, heartbeat percussion, sudden silence, and sharp string hits",
            "theme": "fear, guilt, and survival",
        }
    if any(word in g for word in ["romance", "love"]):
        return {
            "setting": "a rain-washed city where two lives keep crossing at impossible moments",
            "hero_role": "a guarded dreamer afraid of losing love again",
            "ally_role": "a warm-hearted best friend who believes in second chances",
            "antagonist": "time, distance, and one secret that can break everything",
            "threat": "a final goodbye that arrives before the truth can be spoken",
            "visual": "neon cafés, railway platforms, handwritten letters, and emotional close-ups in the rain",
            "music": "soft piano, swelling strings, and a hopeful cinematic rise",
            "theme": "love, sacrifice, timing, and forgiveness",
        }
    if any(word in g for word in ["fantasy", "magic", "myth"]):
        return {
            "setting": "a divided kingdom where magic is disappearing from the world",
            "hero_role": "a reluctant heir with a forbidden gift",
            "ally_role": "a witty mapmaker who knows the hidden roads",
            "antagonist": "a crownless sorcerer stealing power from ancient realms",
            "threat": "the last source of magic dying before the final moon rises",
            "visual": "floating castles, glowing forests, ancient ruins, dragons in storm clouds, and golden magic",
            "music": "epic orchestral drums, choirs, mystical bells, and heroic brass",
            "theme": "destiny, courage, and the cost of power",
        }
    if any(word in g for word in ["crime", "mystery", "detective", "noir"]):
        return {
            "setting": "a corrupt city where every clue leads to someone powerful",
            "hero_role": "a sharp but haunted investigator",
            "ally_role": "a street-smart informant with secrets of their own",
            "antagonist": "a hidden mastermind controlling the city from behind closed doors",
            "threat": "one unsolved case that can expose the entire system",
            "visual": "rainy streets, evidence boards, police lights, dark offices, and tense interrogation rooms",
            "music": "noir piano, pulsing bass, ticking percussion, and suspense strings",
            "theme": "truth, betrayal, justice, and obsession",
        }
    if any(word in g for word in ["action", "adventure", "war"]):
        return {
            "setting": "a global chase across explosive cities, secret bases, and impossible terrain",
            "hero_role": "a former special operative forced back into danger",
            "ally_role": "a brilliant strategist who can hack any system",
            "antagonist": "a ruthless commander planning a world-changing attack",
            "threat": "a countdown that can trigger disaster on a massive scale",
            "visual": "helicopter shots, desert roads, explosions, rooftop fights, and high-speed pursuits",
            "music": "huge trailer drums, aggressive synth bass, brass hits, and rising action pulses",
            "theme": "loyalty, revenge, sacrifice, and courage under pressure",
        }
    if any(word in g for word in ["comedy", "funny"]):
        return {
            "setting": "a chaotic modern city where one small mistake becomes a public disaster",
            "hero_role": "an unlucky but lovable dreamer",
            "ally_role": "an overconfident friend with terrible plans",
            "antagonist": "a rival who turns every situation into a competition",
            "threat": "one ridiculous deadline that could ruin everything",
            "visual": "fast cuts, awkward slow motion, bright streets, messy rooms, and expressive reactions",
            "music": "playful drums, funky bass, comic pauses, and upbeat orchestral hits",
            "theme": "friendship, embarrassment, confidence, and chaos",
        }
    if any(word in g for word in ["drama", "family", "emotional"]):
        return {
            "setting": "a close-knit community where one decision changes an entire family",
            "hero_role": "a determined person carrying an old regret",
            "ally_role": "a family member who refuses to give up on them",
            "antagonist": "the past and the consequences of an unspoken truth",
            "threat": "a final chance to repair what was broken",
            "visual": "warm homes, quiet roads, emotional close-ups, old photographs, and sunset silhouettes",
            "music": "gentle piano, emotional strings, soft percussion, and a hopeful finale",
            "theme": "forgiveness, identity, family, and healing",
        }
    # Default sci-fi / thriller profile.
    return {
        "setting": "a futuristic surveillance city where technology controls everyday life",
        "hero_role": "a brilliant systems architect who starts questioning the world they built",
        "ally_role": "a rogue data-smuggler who has seen the truth from below the city",
        "antagonist": "a powerful AI-backed authority that predicts and controls human choices",
        "threat": "a prediction that turns personal and begins a countdown to disaster",
        "visual": "neon skylines, holographic screens, drones, dark laboratories, and glowing AI cores",
        "music": "dark orchestral synth, ticking percussion, distorted AI tones, and explosive trailer drums",
        "theme": "free will, truth, control, and sacrifice",
    }


def _names(title: str, genre: str) -> tuple[str, str, str, str]:
    first_names = ["Elena", "Aarav", "Maya", "Riya", "Kabir", "Nora", "Ishan", "Zara", "Dev", "Anika"]
    last_names = ["Voss", "Renn", "Malhotra", "Stone", "Rao", "Mehra", "Vale", "Sinha", "Cross", "Arden"]
    seed_text = title + genre
    hero = _pick(first_names, seed_text + "hero") + " " + _pick(last_names, seed_text + "h1")
    ally = _pick(first_names, seed_text + "ally") + " " + _pick(last_names, seed_text + "a1")
    loved_one = _pick(first_names, seed_text + "love") + " " + _pick(last_names, seed_text + "l1")
    villain = _pick(["Director Kael Orin", "Professor Veyra", "Captain Draven", "Minister Solace", "The Architect", "Lord Varun Ash", "Detective Mara Kline"], seed_text + "villain")
    return hero, ally, loved_one, villain


def _extract_field(story: str, field: str, default: str) -> str:
    pattern = rf"\*\*{re.escape(field)}:\*\*\s*(.+)"
    match = re.search(pattern, story)
    return match.group(1).strip() if match else default


def generate_story(movie_title: str, genre: str, idea: str = "") -> str:
    title = _clean(movie_title, "Untitled Future")
    g = _clean(genre, "Sci-Fi Thriller")
    user_idea = _clean(idea, "A mysterious event forces the main character to uncover a hidden truth before time runs out.")
    p = _profile(f"{g} {title} {user_idea}")
    hero, ally, loved_one, villain = _names(title, g + user_idea)

    return dedent(f"""
    # Story Output

    **Movie Title:** {title}  
    **Genre:** {g}  
    **User Idea:** {user_idea}

    ## Story Summary
    **{title}** is a {g.lower()} built around this idea: {user_idea} The story begins in {p['setting']}. At the center is **{hero}**, {p['hero_role']}. {hero.split()[0]} wants a normal life, but the world around them is already changing in ways no one can ignore.

    The first turning point arrives when {user_idea[0].lower() + user_idea[1:] if user_idea else 'a strange incident disrupts everything'} What seems like a personal problem quickly becomes part of something much larger. With the help of **{ally}**, {p['ally_role']}, the hero discovers that **{villain}** is connected to {p['antagonist']}. The danger grows when **{loved_one}** becomes trapped in the middle of the conflict.

    As the trailer builds, the hero is forced to choose between staying safe and exposing the truth. The final act pushes them toward {p['threat']}. In the end, **{title}** becomes a cinematic journey about {p['theme']}. The question driving the movie is simple: when the world decides your fate, will you accept it or fight back?

    ## Main Characters
    - **{hero}** – {p['hero_role'].capitalize()}.
    - **{ally}** – {p['ally_role'].capitalize()}.
    - **{loved_one}** – The emotional reason the hero cannot walk away.
    - **{villain}** – The force behind the central danger.

    ## Setting
    {p['setting'].capitalize()}. Visual style: {p['visual']}.

    ## Central Conflict
    {hero.split()[0]} must stop {p['threat']} while facing {p['antagonist']}.
    """).strip()


def generate_trailer_script(story: str, movie_title: str = "", genre: str = "", idea: str = "") -> str:
    title = _clean(movie_title or _extract_field(story, "Movie Title", "Untitled Future"), "Untitled Future")
    g = _clean(genre or _extract_field(story, "Genre", "Sci-Fi Thriller"), "Sci-Fi Thriller")
    user_idea = _clean(idea or _extract_field(story, "User Idea", "a secret that changes everything"), "a secret that changes everything")
    idea_sentence = user_idea.rstrip(".!?")
    p = _profile(f"{g} {title} {user_idea}")
    hero, ally, loved_one, villain = _names(title, g + user_idea)

    return dedent(f"""
    # Trailer Script Output

    ## Scene 1 – The World Before the Fall
    **Visual Description:** A cinematic establishing shot of {p['setting']}, filled with {p['visual']}. The camera slowly pushes forward as the world appears beautiful but uneasy.
    **Narration:** “Every story begins with a world that believes it is safe.”

    ## Scene 2 – The Idea Becomes Real
    **Visual Description:** {hero} discovers the first sign of the central idea: {idea_sentence}. The world reacts through sudden omens, tense close-ups, frightened crowds, and visual details connected to {p['visual']}.
    **Narration:** “But one impossible moment can turn an ordinary life into a fight for everything.”

    ## Scene 3 – The Hidden Enemy
    **Visual Description:** {villain} is revealed through dramatic shadows, secret files, and tense close-ups. {ally} warns the hero that the danger is bigger than anyone imagined.
    **Narration:** “Behind the truth stands an enemy who has already planned the ending.”

    ## Scene 4 – No Way Back
    **Visual Description:** {hero}, {ally}, and {loved_one} are thrown into a high-stakes sequence: running through danger, facing betrayal, and choosing between fear and courage.
    **Narration:** “Now the only way to survive is to challenge the fate written for them.”

    ## Scene 5 – Final Choice
    **Visual Description:** In a dramatic final location, the hero confronts {p['threat']}. The screen cuts between emotional close-ups, rising chaos, and the title reveal: {title}.
    **Narration:** “This is not just their story. This is the moment destiny changes. {title}. What would you risk to rewrite tomorrow?”

    ## Background Music Mood
    {p['music']}.
    """).strip()


def extract_narration(trailer_script: str) -> str:
    matches = re.findall(r"\*\*Narration:\*\*\s*[“\"](.+?)[”\"]", trailer_script)
    if not matches:
        matches = re.findall(r"Narration:\s*[“\"]?(.+?)[”\"]?$", trailer_script, flags=re.M)
    return " ".join(line.strip() for line in matches).strip()


def generate_image_prompts(trailer_script: str) -> str:
    scenes = re.findall(
        r"##\s+Scene\s+(\d+).*?\n\*\*Visual Description:\*\*\s*(.*?)(?:\n\*\*Narration|\Z)",
        trailer_script,
        flags=re.S,
    )
    if not scenes:
        scenes = [("1", "A cinematic movie trailer scene with dramatic lighting.")]

    lines = ["# AI Image Generation Prompts"]
    for number, description in scenes[:5]:
        clean = " ".join(description.split())
        lines.append(
            f"\n## Scene {number}\n{clean} Cinematic 4K film still, dramatic lighting, "
            "anamorphic lens, high contrast, detailed environment, emotional mood, "
            "professional movie trailer composition, no text, 16:9."
        )
    return "\n".join(lines).strip()
