from fastapi import APIRouter, Request

from db.database import (
    get_encryption_breakdown,
    get_hidden_count,
    get_network_count,
    get_observation_count,
    list_databases,
)
from gui.common import open_database, render

router = APIRouter(prefix="/statistics")


@router.get("")
def select_database(request: Request):
    return render(
        request,
        "select_database.html",
        active="statistics",
        section="STATISTICS",
        title="STATISTICS",
        databases=list_databases(),
        base_url="/statistics",
        back="/",
    )


@router.get("/{city}")
def statistics(request: Request, city: str):
    with open_database(city) as connection:
        networks = get_network_count(connection)
        observations = get_observation_count(connection)
        hidden = get_hidden_count(connection)
        breakdown = get_encryption_breakdown(connection)

    return render(
        request,
        "statistics.html",
        active="statistics",
        section=f"STATISTICS // {city}",
        title=city,
        back="/statistics",
        networks=networks,
        observations=observations,
        hidden=hidden,
        breakdown=[
            (encryption, count, count * 100 / networks if networks else 0)
            for encryption, count in breakdown
        ],
    )
