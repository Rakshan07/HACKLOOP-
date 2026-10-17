"""Gemma Story Engine: coordinates prompts, API calls, parsing, and fallbacks."""
import logging
from .client import GemmaClient, GemmaClientError
from .config import Settings, get_settings
from .prompts import SYSTEM_INSTRUCTION, build_ending_prompt, build_scene_prompt
from .schemas import Article, Choice, Ending, Scene, StoryStep

logger = logging.getLogger("gemma_service.engine")


class GemmaStoryEngine:
    """Core story generation engine powering RabbitHole with Gemma."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.client = GemmaClient(self.settings)

    def _generate_mock_scene(self, article: Article, steps: list[StoryStep], turn: int) -> Scene:
        """Dynamic fallback scene generator when offline or mock mode is enabled."""
        sentences = [s.strip() for s in article.extract.replace("\n", " ").split(". ") if len(s.strip()) > 15]
        fact = sentences[0] + "." if sentences else f"{article.title} holds a remarkable history."

        last_action = steps[-1].chosen_text if steps else "arriving at the threshold"

        narrative_templates = {
            1: (
                f"You step into the unfolding world of '{article.title}'. "
                f"The environment is thick with anticipation as clues hint at a forgotten mystery. "
                f"A path lies ahead, but rumors suggest caution."
            ),
            2: (
                f"Following your decision to {last_action.lower()}, unexpected signs appear. "
                f"Details mentioned in historical records begin aligning with your surroundings, "
                f"raising new questions about what was left behind."
            ),
            3: (
                f"Having chosen to {last_action.lower()}, you stumble upon an intricate mechanism or archive. "
                f"Documents concerning '{article.title}' shed light on an overlooked connection, "
                f"drawing you deeper into the rabbit hole."
            ),
            4: (
                f"The stakes heighten dramatically after you chose to {last_action.lower()}. "
                f"Time is running short, and contradictory evidence demands an urgent, calculated move."
            ),
            5: (
                f"Everything has led to this moment. Having chosen to {last_action.lower()}, "
                f"you stand before the pivotal threshold of '{article.title}'. "
                f"Your final choice will determine how this chapter closes."
            ),
        }

        narrative = narrative_templates.get(
            turn,
            f"You continue your journey through {article.title}, dealing with the consequences of having chosen to {last_action.lower()}."
        )

        choices = [
            Choice(id="A", text=f"Investigate the direct historical evidence of {article.title}"),
            Choice(id="B", text="Seek guidance from local accounts or related records"),
            Choice(id="C", text="Take an unconventional risk to decipher the core anomaly"),
        ]

        return Scene(turn=turn, narrative=narrative, choices=choices, fact=fact)

    def _generate_mock_ending(self, article: Article, steps: list[StoryStep]) -> Ending:
        """Dynamic fallback ending generator when offline or mock mode is enabled."""
        sentences = [s.strip() for s in article.extract.replace("\n", " ").split(". ") if len(s.strip()) > 15]
        lesson_fact = sentences[1] + "." if len(sentences) > 1 else (sentences[0] + "." if sentences else article.title)

        return Ending(
            title=f"The Legacy of {article.title}",
            narrative=(
                f"Your 5-step expedition through '{article.title}' comes to a profound close. "
                f"From your earliest choice to your final breakthrough, you unveiled truths once lost to time. "
                f"The journey demonstrated how curiosity transforms simple facts into living history."
            ),
            lesson=f"Real-world takeaway: {lesson_fact}",
        )

    async def generate_scene(self, article: Article, steps: list[StoryStep], turn: int) -> Scene:
        """Generate an adventure scene with choices for the specified turn."""
        if not self.settings.mock_mode and self.settings.gemini_api_key:
            try:
                prompt = build_scene_prompt(article, steps, turn)
                data = await self.client.generate_text(SYSTEM_INSTRUCTION, prompt)

                # Ensure choices match schema
                raw_choices = data.get("choices", [])
                formatted_choices: list[Choice] = []
                for idx, cid in enumerate(["A", "B", "C"]):
                    if idx < len(raw_choices):
                        text = raw_choices[idx].get("text", f"Explore branch {cid}")
                    else:
                        text = f"Examine alternate lead {cid}"
                    formatted_choices.append(Choice(id=cid, text=text))

                narrative = data.get("narrative", f"You continue through {article.title}.")
                fact = data.get("fact", f"{article.title} is documented in Wikipedia archives.")

                return Scene(
                    turn=turn,
                    narrative=narrative,
                    choices=formatted_choices,
                    fact=fact,
                )
            except GemmaClientError as exc:
                logger.warning("Gemma client error; falling back to offline generator: %s", exc)

        return self._generate_mock_scene(article, steps, turn)

    async def generate_ending(self, article: Article, steps: list[StoryStep]) -> Ending:
        """Generate the story epilogue after turn 5."""
        if not self.settings.mock_mode and self.settings.gemini_api_key:
            try:
                prompt = build_ending_prompt(article, steps)
                data = await self.client.generate_text(SYSTEM_INSTRUCTION, prompt)
                return Ending(
                    title=data.get("title", f"Epilogue of {article.title}"),
                    narrative=data.get("narrative", f"Your quest regarding {article.title} has completed."),
                    lesson=data.get("lesson", f"Historical significance: {article.title}"),
                )
            except GemmaClientError as exc:
                logger.warning("Gemma client error; falling back to offline ending generator: %s", exc)

        return self._generate_mock_ending(article, steps)


# Module-level convenience functions adhering to Member 4 contract
_default_engine: GemmaStoryEngine | None = None


def _get_engine() -> GemmaStoryEngine:
    global _default_engine
    if _default_engine is None:
        _default_engine = GemmaStoryEngine()
    return _default_engine


async def generate_scene(article: Article, steps: list[StoryStep], turn: int) -> Scene:
    return await _get_engine().generate_scene(article, steps, turn)


async def generate_ending(article: Article, steps: list[StoryStep]) -> Ending:
    return await _get_engine().generate_ending(article, steps)
