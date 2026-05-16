import os
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse


MAX_REQUEST_BYTES = int(os.getenv("MAX_REQUEST_BYTES", str(25 * 1024 * 1024)))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

_requests: dict[str, deque[float]] = defaultdict(deque)


def admin_auth_required() -> bool:
    return bool(os.getenv("ADMIN_API_KEY")) or os.getenv("ENV", "").lower() == "production"


def require_admin(request: Request) -> None:
    expected = os.getenv("ADMIN_API_KEY")
    if not admin_auth_required():
        return
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_API_KEY is required in production.",
        )

    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = auth.split(" ", 1)[1].strip()
    if token != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid bearer token")


AdminDependency = Depends(require_admin)


async def request_size_middleware(request: Request, call_next: Callable):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BYTES:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Request body too large"},
        )
    return await call_next(request)


async def rate_limit_middleware(request: Request, call_next: Callable):
    client = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    bucket = _requests[client]
    while bucket and bucket[0] < window_start:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded"},
        )
    bucket.append(now)
    return await call_next(request)


def production_config_errors() -> list[str]:
    if os.getenv("ENV", "").lower() != "production":
        return []

    errors = []
    for key in ("OPENAI_API_KEY", "FRONTEND_URL", "BACKEND_URL", "ADMIN_API_KEY"):
        if not os.getenv(key):
            errors.append(f"{key} is required in production")
    if not (os.getenv("JWT_SECRET") or os.getenv("SESSION_SECRET")):
        errors.append("JWT_SECRET or SESSION_SECRET is required in production")
    return errors


def path_writable(path: str) -> bool:
    p = Path(path)
    target = p if p.suffix == "" else p.parent
    try:
        target.mkdir(parents=True, exist_ok=True)
        probe = target / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except Exception:
        return False
