import pytest
from fastapi.testclient import TestClient
from gemma_service.server import app

client = TestClient(app)


def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "RabbitHole" in data["service"]


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "model" in data


def test_generate_scene_endpoint():
    payload = {
        "article": {
            "title": "Marie Curie",
            "extract": "Marie Salomea Sklodowska Curie was a Polish and naturalised-French physicist and chemist who conducted pioneering research on radioactivity.",
            "url": "https://en.wikipedia.org/wiki/Marie_Curie",
        },
        "steps": [],
        "turn": 1,
    }
    res = client.post("/api/v1/gemma/scene", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["turn"] == 1
    assert "narrative" in data
    assert len(data["choices"]) == 3
    assert data["choices"][0]["id"] == "A"


def test_generate_ending_endpoint():
    payload = {
        "article": {
            "title": "Marie Curie",
            "extract": "Marie Salomea Sklodowska Curie was a Polish and naturalised-French physicist and chemist who conducted pioneering research on radioactivity.",
            "url": "https://en.wikipedia.org/wiki/Marie_Curie",
        },
        "steps": [
            {
                "turn": 1,
                "narrative": "Discovered unknown radiation emissions in laboratory.",
                "choices": [
                    {"id": "A", "text": "Isolate the pitchblende ore"},
                    {"id": "B", "text": "Consult peer scientists"},
                    {"id": "C", "text": "Calibrate electrometer"},
                ],
                "chosenId": "A",
                "chosenText": "Isolate the pitchblende ore",
            }
        ],
    }
    res = client.post("/api/v1/gemma/ending", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "title" in data
    assert "narrative" in data
    assert "lesson" in data
