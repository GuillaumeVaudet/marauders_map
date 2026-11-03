from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from sqlite3 import Connection
from typing import NamedTuple

from fastapi import HTTPException, Request
from fastapi.templating import Jinja2Templates

from db.database import connect, list_databases

PAGE_SIZE = 50
RSSI_FLOOR = -100
RSSI_CEILING = -30


class Toast(NamedTuple):
    message: str
    level: str = "information"


@dataclass
class Page:
    rows: Sequence
    number: int
    count: int
    total: int

    @property
    def has_previous(self) -> bool:
        return self.number > 1

    @property
    def has_next(self) -> bool:
        return self.number < self.count


def rssi_percent(rssi: int | None) -> int:
    """Convert a dBm value to the width of a signal meter."""
    if rssi is None:
        return 0
    span = RSSI_CEILING - RSSI_FLOOR
    return max(0, min(100, round((rssi - RSSI_FLOOR) * 100 / span)))


def file_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB"):
        if value < 1024:
            return f"{value:.0f} {unit}"
        value /= 1024
    return f"{value:.1f} GB"


templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
templates.env.filters["rssi_percent"] = rssi_percent
templates.env.filters["file_size"] = file_size


def render(
    request: Request,
    template: str,
    *,
    status_code: int = 200,
    push_url: str | None = None,
    toast: Toast | None = None,
    **context,
):
    context["toast"] = toast
    headers = {"HX-Push-Url": push_url} if push_url else None
    return templates.TemplateResponse(
        request, template, context, status_code=status_code, headers=headers
    )


def wants_results_only(request: Request) -> bool:
    """True when HTMX only asks to refresh the results of the current table."""
    return request.headers.get("hx-target") == "results"


def paginate(rows: Sequence, page: int) -> Page:
    total = len(rows)
    count = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    number = max(1, min(page, count))
    start = (number - 1) * PAGE_SIZE
    return Page(rows[start:start + PAGE_SIZE], number, count, total)


def require_database(city: str) -> None:
    """Accept any city, as long as it is one of the existing databases."""
    if city not in list_databases():
        raise HTTPException(404, f"Database not found: {city}")


def is_valid_new_name(city: str) -> bool:
    """Accept any city name, as long as it stays inside the data folder."""
    has_control_character = any(ord(character) < 32 for character in city)
    return not (
        has_control_character
        or "/" in city
        or "\\" in city
        or city.startswith(".")
    )


@contextmanager
def open_database(city: str) -> Iterator[Connection]:
    require_database(city)
    connection = connect(city)
    try:
        yield connection
    finally:
        connection.close()
