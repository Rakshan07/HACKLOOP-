"""FastAPI microservice for standalone Gemma Story Engine."""
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .engine import GemmaStoryEngine
from .schemas import (
    Ending,
    GenerateEndingRequest,
    GenerateSceneRequest,
    HealthResponse,
    Scene,
)

settings = get_settings()
engine = GemmaStoryEngine(settings)

app = FastAPI(
    title="RabbitHole Gemma AI Service",
    description="Dedicated Gemma-powered interactive storytelling microservice for Wikipedia adventures.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Info"])
async def root():
    return {
        "service": "RabbitHole Gemma Story Engine",
        "model": settings.gemma_model,
        "mock_mode": settings.mock_mode,
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="ok",
        model=settings.gemma_model,
        mock_mode=settings.mock_mode,
        api_key_configured=bool(settings.gemini_api_key),
    )


@app.post("/api/v1/gemma/scene", response_model=Scene, tags=["Story Generation"])
async def generate_scene_endpoint(req: GenerateSceneRequest):
    """Generate the next turn's interactive scene with choices."""
    try:
        return await engine.generate_scene(req.article, req.steps, req.turn)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scene generation failed: {exc}",
        ) from exc


@app.post("/api/v1/gemma/ending", response_model=Ending, tags=["Story Generation"])
async def generate_ending_endpoint(req: GenerateEndingRequest):
    """Generate the final story ending and historical takeaway."""
    try:
        return await engine.generate_ending(req.article, req.steps)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ending generation failed: {exc}",
        ) from exc


def main():
    uvicorn.run(
        "gemma_service.server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
