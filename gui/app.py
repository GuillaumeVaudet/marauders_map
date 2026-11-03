import sqlite3
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from gui.common import render
from gui.routes import data_manager, map as map_view, menu, network, statistics

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

# SSIDs come from captured radio frames, so they are untrusted: this policy
# backs up template escaping by blocking inline and third-party scripts.
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; worker-src 'self' blob:; "  # needed by MapLibre
    "base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
)
CACHEABLE_PREFIXES = ("/static/", "/map/tiles/")

app = FastAPI(
    title="Marauders Map",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.middleware("http")
async def protect_local_app(request: Request, call_next):
    """Refuse changes requested by another website open in the same browser."""
    if request.method not in SAFE_METHODS:
        origin = request.headers.get("origin")
        fetch_site = request.headers.get("sec-fetch-site")
        foreign_origin = origin and urlsplit(origin).netloc != request.headers.get("host")
        if foreign_origin or fetch_site == "cross-site":
            return PlainTextResponse("Cross-site request refused", status_code=403)

    response = await call_next(request)
    response.headers["Content-Security-Policy"] = CONTENT_SECURITY_POLICY
    response.headers["X-Content-Type-Options"] = "nosniff"
    if not request.url.path.startswith(CACHEABLE_PREFIXES):
        response.headers["Cache-Control"] = "no-store"
    return response


# Added last so that it runs first: blocks requests sent through DNS rebinding.
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])


@app.exception_handler(HTTPException)
async def http_error(request: Request, error: HTTPException):
    return render(
        request,
        "message.html",
        status_code=error.status_code,
        section="ERROR",
        title=f"ERROR {error.status_code}",
        message=error.detail,
        back="/",
    )


@app.exception_handler(sqlite3.OperationalError)
async def database_error(request: Request, error: sqlite3.OperationalError):
    return render(
        request,
        "message.html",
        status_code=500,
        section="ERROR",
        title="DATABASE ERROR",
        message=f"This database cannot be read: {error}",
        hint="A database created empty has no networks until a capture is imported.",
        back="/",
    )


app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)
app.mount(
    "/map/tiles",
    StaticFiles(directory=map_view.MAPS_DIRECTORY, check_dir=False),
    name="map-tiles",
)
app.include_router(menu.router)
app.include_router(map_view.router)
app.include_router(network.router)
app.include_router(statistics.router)
app.include_router(data_manager.router)
