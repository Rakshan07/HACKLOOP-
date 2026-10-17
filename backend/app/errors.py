"""One standard error type for the whole backend. Owner: Member 3 (frozen contract)."""


class AppError(Exception):
    """Raise this anywhere. main.py turns it into {"error": {code, message, retryable}}."""

    def __init__(self, code: str, message: str, status_code: int = 400, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.message = message  # always friendly: this is shown to players
        self.status_code = status_code
        self.retryable = retryable
