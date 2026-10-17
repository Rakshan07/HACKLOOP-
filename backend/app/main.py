"""HTTP routes. Owner: Member 3. Run: uvicorn app.main:app --reload --port 8000"""
import logging
from pathlib import Path
from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from . import game_service
from .config import get_settings
from .errors import AppError
from .schemas import ChoiceRequest, GameView

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("rabbit")
settings = get_settings()

app = FastAPI(title="Rabbit Hole API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def error_response(status: int, code: str, message: str, retryable: bool) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, "retryable": retryable}},
    )


@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError):
    return error_response(exc.status_code, exc.code, exc.message, exc.retryable)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_: Request, __: RequestValidationError):
    return error_response(422, "BAD_REQUEST", "That request was not valid.", False)


@app.exception_handler(StarletteHTTPException)
async def handle_http_error(_: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return error_response(404, "NOT_FOUND", "That address does not exist.", False)
    return error_response(
        exc.status_code, "HTTP_ERROR", "The request could not be completed.", False
    )


@app.exception_handler(Exception)
async def handle_unexpected(_: Request, exc: Exception):
    log.exception("Unexpected error: %s", type(exc).__name__)  # details stay in the server log
    return error_response(
        500, "INTERNAL", "Something went wrong on our side. Please try again.", True
    )


router = APIRouter(prefix="/api")


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "model": settings.gemma_model,
        "aiConfigured": bool(settings.gemini_api_key),
    }


@router.post("/games", response_model=GameView, status_code=201)
async def create_game():
    return await game_service.create_game()


@router.get("/games/{game_id}", response_model=GameView)
async def get_game(game_id: str):
    return game_service.get_view(game_id)


@router.post("/games/{game_id}/start", response_model=GameView)
async def start_game(game_id: str):
    return await game_service.begin(game_id)


@router.post("/games/{game_id}/choices", response_model=GameView)
async def choose(game_id: str, body: ChoiceRequest):
    return await game_service.choose(game_id, body.turn, body.choice_id)


@router.post("/games/{game_id}/restart", response_model=GameView, status_code=201)
async def restart_game(game_id: str):
    return await game_service.restart_same_topic(game_id)


app.include_router(router)

# One-command deploy: if the frontend has been built, serve it from this same server.
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")
