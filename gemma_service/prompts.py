"""Prompt construction and templates for Gemma Story Engine."""
import json
from .schemas import Article, StoryStep

SYSTEM_INSTRUCTION = """You are an expert interactive fiction writer and educational storyteller for an adventure game called "RabbitHole".
Your goal is to weave an immersive, suspenseful, and educational choose-your-own-adventure narrative based directly on real Wikipedia topics.

Core Rules:
1. Grounding: All story events, puzzles, and choices MUST be anchored in the provided Wikipedia extract.
2. Structure: Every scene must provide a vivid narrative (2-4 paragraphs), exactly 3 meaningful choices labeled "A", "B", and "C", and 1 genuine educational fact verified by the article extract.
3. Turn Progression:
   - Turn 1 (Arrival): Establish the world, mystery, and immediate dilemma.
   - Turn 2 (Complication): The mystery deepens; first obstacle appears.
   - Turn 3 (Discovery): Uncover a pivotal artifact, clue, or historical truth.
   - Turn 4 (High Stakes): Tense situation where past choices culminate.
   - Turn 5 (Climax): The critical threshold before the adventure resolves.
4. Output format: You must respond ONLY with raw, valid JSON. Do not include markdown codeblocks or other commentary outside the JSON object.
"""


def format_history(steps: list[StoryStep]) -> str:
    """Format player choice history as structured text context."""
    if not steps:
        return "This is the very beginning of the adventure (no prior turns)."

    history_lines = ["Story So Far:"]
    for step in steps:
        history_lines.append(f"- Turn {step.turn}:")
        history_lines.append(f"  Narrative snippet: {step.narrative[:180]}...")
        history_lines.append(f"  Player chose ({step.chosen_id}): {step.chosen_text}")
    return "\n".join(history_lines)


def build_scene_prompt(article: Article, steps: list[StoryStep], turn: int) -> str:
    """Build the prompt requesting Gemma to write the next scene."""
    history = format_history(steps)

    turn_goals = {
        1: "Establish the setting and introduce the opening curiosity or challenge.",
        2: "Introduce a complication based on the player's initial choice.",
        3: "Unveil a deeper secret or unexpected turn of events.",
        4: "Escalate the stakes with a difficult moral, intellectual, or survival dilemma.",
        5: "Reach the climax: the player must make their ultimate deciding move.",
    }
    goal = turn_goals.get(turn, "Advance the adventure with high engagement.")

    return f"""Topic: {article.title}
Article Extract:
\"\"\"{article.extract}\"\"\"

{history}

Current Turn: {turn} of 5
Turn Goal: {goal}

Generate the scene for Turn {turn}. You must output ONLY a valid JSON object with the following exact keys:
{{
  "narrative": "Vivid narrative of what happens now, honoring the player's last choice and setting up this turn's dilemma.",
  "choices": [
    {{"id": "A", "text": "First proactive choice"}},
    {{"id": "B", "text": "Second distinct alternative choice"}},
    {{"id": "C", "text": "Third bold or unconventional choice"}}
  ],
  "fact": "A fascinating real fact drawn directly from the Wikipedia article extract that connects to this moment."
}}
"""


def build_ending_prompt(article: Article, steps: list[StoryStep]) -> str:
    """Build the prompt requesting Gemma to write the adventure conclusion."""
    history = format_history(steps)

    return f"""Topic: {article.title}
Article Extract:
\"\"\"{article.extract}\"\"\"

Complete Player Journey:
{history}

The player has finished all 5 turns. Write a memorable, satisfying conclusion to their story based on the path they carved.

You must output ONLY a valid JSON object with the following exact keys:
{{
  "title": "A compelling epilogue title",
  "narrative": "A rich 2-3 paragraph epilogue showing the final outcome, consequences, and lasting impression of the adventure.",
  "lesson": "A thoughtful takeaway summarizing the true historical or scientific significance of {article.title} based on the Wikipedia article."
}}
"""
