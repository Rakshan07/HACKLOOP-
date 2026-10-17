"""Interactive CLI to play and test Gemma Story Engine in terminal."""
import asyncio
import sys
from .engine import GemmaStoryEngine
from .schemas import Article, Choice, ChoiceId, StoryStep, TOTAL_TURNS

SAMPLE_ARTICLE = Article(
    title="Library of Alexandria",
    extract=(
        "The Great Library of Alexandria in Alexandria, Egypt, was one of the largest and most significant libraries "
        "of the ancient world. The Library was part of a larger research institution called the Mouseion, dedicated "
        "to the Muses, the nine goddesses of the arts. Despite the widespread belief that the Library was burned "
        "once and cataclysmically destroyed, the Library actually declined gradually over several centuries, starting "
        "with the purging of intellectuals from Alexandria in 145 BC during the reign of Ptolemy VIII Physcon. "
        "Julius Caesar inadvertently burned part of the library during his civil war in 48 BC."
    ),
    url="https://en.wikipedia.org/wiki/Library_of_Alexandria",
)


async def run_adventure():
    engine = GemmaStoryEngine()
    print("=" * 60)
    print(" 📖 RABBITHOLE: GEMMA STORY ENGINE CLI DEMO")
    print("=" * 60)
    print(f"Topic: {SAMPLE_ARTICLE.title}")
    print(f"Model: {engine.settings.gemma_model} (Mock mode: {engine.settings.mock_mode})")
    print("-" * 60)

    steps: list[StoryStep] = []

    for turn in range(1, TOTAL_TURNS + 1):
        print(f"\n[Generating Turn {turn}/{TOTAL_TURNS} with Gemma...]")
        scene = await engine.generate_scene(SAMPLE_ARTICLE, steps, turn)

        print("\n" + "=" * 50)
        print(f"📍 TURN {scene.turn} / {TOTAL_TURNS}")
        print("=" * 50)
        print(f"\n{scene.narrative}\n")
        print(f"💡 Fact: {scene.fact}\n")

        print("Choices:")
        for ch in scene.choices:
            print(f"  [{ch.id}] {ch.text}")

        # Choose automatically if non-interactive or ask user
        valid_choice = False
        chosen_id: ChoiceId = "A"
        chosen_choice: Choice = scene.choices[0]

        while not valid_choice:
            try:
                pick = input("\nSelect choice (A/B/C) or press Enter for A: ").strip().upper()
                if not pick:
                    pick = "A"
                match = next((c for c in scene.choices if c.id == pick), None)
                if match:
                    chosen_id = match.id  # type: ignore
                    chosen_choice = match
                    valid_choice = True
                else:
                    print("Invalid choice, please enter A, B, or C.")
            except (EOFError, KeyboardInterrupt):
                print("\nDefaulting to choice A.")
                chosen_id = "A"
                chosen_choice = scene.choices[0]
                valid_choice = True

        steps.append(
            StoryStep(
                turn=scene.turn,
                narrative=scene.narrative,
                choices=scene.choices,
                chosen_id=chosen_id,
                chosen_text=chosen_choice.text,
            )
        )

    print("\n[Writing adventure ending with Gemma...]")
    ending = await engine.generate_ending(SAMPLE_ARTICLE, steps)

    print("\n" + "#" * 60)
    print(f" 🏆 EPILOGUE: {ending.title.upper()}")
    print("#" * 60)
    print(f"\n{ending.narrative}\n")
    print(f"🎓 Lesson: {ending.lesson}")
    print("#" * 60)


def main():
    try:
        asyncio.run(run_adventure())
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
