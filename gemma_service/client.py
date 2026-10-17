"""Gemma API Client for Google Generative Language API with fallback/mock capabilities."""
import json
import logging
import re
from typing import Any
import httpx
from .config import Settings

logger = logging.getLogger("gemma_service.client")


class GemmaClientError(Exception):
    """Raised when communication with Gemma API fails."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


class GemmaClient:
    """Handles communication with Gemma models via Google AI API."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.gemma_model}:generateContent"
        )

    def _extract_json(self, raw_text: str) -> dict[str, Any]:
        """Strip markdown fences and parse the JSON payload reliably."""
        text = raw_text.strip()

        # Handle ```json ... ``` blocks
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        # If still not starting with {, search for outermost JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)

        try:
            return json.loads(text)
        except json.JSONDecodeError as err:
            logger.error("Failed to parse JSON response: %s | Raw: %s", err, raw_text)
            raise GemmaClientError(f"Model returned malformed JSON: {err}") from err

    async def generate_text(self, system_instruction: str, user_prompt: str) -> dict[str, Any]:
        """Send prompt to Gemma model and return parsed JSON result."""
        if self.settings.mock_mode or not self.settings.gemini_api_key:
            logger.info("Using mock response generator (mock_mode=%s)", self.settings.mock_mode)
            raise GemmaClientError("Mock mode active - use engine fallback", status_code=200)

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_instruction}\n\n{user_prompt}"}],
                }
            ],
            "generationConfig": {
                "temperature": self.settings.gemma_temperature,
                "maxOutputTokens": self.settings.gemma_max_output_tokens,
                "responseMimeType": "application/json",
            },
        }

        headers = {
            "Content-Type": "application/json",
        }
        params = {"key": self.settings.gemini_api_key}

        async with httpx.AsyncClient(timeout=self.settings.gemma_timeout_seconds) as client:
            try:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    params=params,
                )
            except httpx.TimeoutException as exc:
                logger.error("Gemma API request timed out after %s seconds", self.settings.gemma_timeout_seconds)
                raise GemmaClientError("AI generation timed out", status_code=504) from exc
            except httpx.RequestError as exc:
                logger.error("Network error while connecting to Gemma API: %s", exc)
                raise GemmaClientError(f"Network error: {exc}", status_code=502) from exc

        if response.status_code != 200:
            logger.error("Gemma API responded with status %s: %s", response.status_code, response.text)
            raise GemmaClientError(
                f"Gemma API error ({response.status_code}): {response.text}",
                status_code=response.status_code,
            )

        data = response.json()
        try:
            candidates = data.get("candidates", [])
            if not candidates:
                raise GemmaClientError("No content candidates returned by Gemma model")
            first_candidate = candidates[0]
            parts = first_candidate.get("content", {}).get("parts", [])
            if not parts or "text" not in parts[0]:
                raise GemmaClientError("Missing text part in Gemma response candidate")
            raw_output = parts[0]["text"]
            return self._extract_json(raw_output)
        except (KeyError, IndexError) as exc:
            raise GemmaClientError(f"Unexpected API response structure: {exc}") from exc
