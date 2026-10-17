# RabbitHole: Gemma AI Story Engine 🔮

This repository branch (`GEMMA`) houses the dedicated **Gemma AI Story Engine** for the **RabbitHole** interactive Wikipedia adventure game.

It translates real Wikipedia articles into branching, immersive 5-turn choose-your-own-adventure stories powered by **Google Gemma** models (such as `gemma-4-26b-a4b-it` or `gemma-4-31b-it`) via the Gemini API, with automatic offline fallback support for seamless development.

---

## 🏗️ Architecture

```
.vscode/
├── gemma_service/
│   ├── __init__.py      # Package entrypoint (generate_scene, generate_ending, GemmaStoryEngine)
│   ├── config.py        # Settings loaded from environment / .env
│   ├── schemas.py       # Pydantic schemas adhering to team contract (camelCase JSON)
│   ├── prompts.py       # Turn-aware prompt engineering with strict JSON output specs
│   ├── client.py        # Async HTTP client with JSON parsing & error handling
│   ├── engine.py        # Core story coordinator with dynamic offline/mock generators
│   ├── server.py        # FastAPI microservice for HTTP consumption
│   └── cli.py           # Interactive terminal adventure demo
├── tests/
│   ├── test_schemas.py  # Contract and validation tests
│   ├── test_prompts.py  # Prompt assembly tests
│   ├── test_engine.py   # Story engine unit tests
│   └── test_server.py   # FastAPI endpoint tests
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
└── README.md
```

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and optionally set your Gemini API key:
```env
GEMINI_API_KEY=your_key_here
GEMMA_MODEL=gemma-4-26b-a4b-it
```
*(If no API key is provided, the engine automatically runs in resilient mock mode, allowing full local testing without quota limitations).*

### 3. Play the Adventure in CLI
Experience a complete 5-turn Wikipedia adventure in your terminal:
```bash
python -m gemma_service.cli
```

### 4. Run the Standalone Microservice
Launch the FastAPI server on `http://localhost:8001`:
```bash
python -m uvicorn gemma_service.server:app --reload --port 8001
```
Interactive Swagger docs: `http://localhost:8001/docs`

---

## 🔌 API Endpoints

### `POST /api/v1/gemma/scene`
Generates the next scene and 3 choices based on the Wikipedia article and previous player choices.
- **Payload**:
  ```json
  {
    "article": {
      "title": "Library of Alexandria",
      "extract": "The Great Library of Alexandria in Alexandria, Egypt...",
      "url": "https://en.wikipedia.org/wiki/Library_of_Alexandria"
    },
    "steps": [],
    "turn": 1
  }
  ```
- **Response**:
  ```json
  {
    "turn": 1,
    "narrative": "You step into the great colonnade...",
    "choices": [
      { "id": "A", "text": "Search the parchment archives" },
      { "id": "B", "text": "Inquire with the head scholar" },
      { "id": "C", "text": "Investigate the restricted vault" }
    ],
    "fact": "The library declined gradually over several centuries."
  }
  ```

### `POST /api/v1/gemma/ending`
Generates the story resolution and real-world lesson after all 5 turns have completed.
- **Response**:
  ```json
  {
    "title": "The Last Scholar of Alexandria",
    "narrative": "Having made your final decision...",
    "lesson": "Julius Caesar inadvertently burned part of the library during his civil war in 48 BC."
  }
  ```

---

## 🧪 Running Tests

Run the full pytest suite:
```bash
pytest -v
```