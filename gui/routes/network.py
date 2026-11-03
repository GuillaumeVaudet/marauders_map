from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request

from db.database import get_networks, get_observations, list_databases
from gui.common import open_database, paginate, render, wants_results_only

router = APIRouter(prefix="/networks")


@router.get("")
def select_database(request: Request):
    return render(
        request,
        "select_database.html",
        active="networks",
        section="NETWORKS",
        title="NETWORKS",
        databases=list_databases(),
        base_url="/networks",
        back="/",
    )


@router.get("/{city}")
def network_list(request: Request, city: str, q: str = "", page: int = 1):
    with open_database(city) as connection:
        networks = get_networks(connection)

    search = q.strip().casefold()
    if search:
        networks = [
            network for network in networks
            if any(search in column.casefold() for column in network)
        ]

    context = {"city": city, "q": q, "results": paginate(networks, page)}
    if wants_results_only(request):
        return render(request, "partials/network_results.html", **context)
    return render(
        request,
        "network_list.html",
        active="networks",
        section=f"NETWORKS // {city}",
        title=city,
        back="/networks",
        **context,
    )


@router.get("/{city}/{bssid}")
def network_detail(request: Request, city: str, bssid: str, page: int = 1):
    with open_database(city) as connection:
        network = next(
            (row for row in get_networks(connection) if row[0] == bssid),
            None,
        )
        if network is None:
            raise HTTPException(404, f"Network not found: {bssid}")
        observations = get_observations(connection, bssid)

    measured = [row[3] for row in observations if row[3] is not None]
    context = {
        "city": city,
        "network": network,
        "results": paginate(observations, page),
        "strongest": max(measured, default=None),
    }
    if wants_results_only(request):
        return render(request, "partials/observation_results.html", **context)
    return render(
        request,
        "network_detail.html",
        active="networks",
        section=f"NETWORKS // {city} // OBSERVATIONS",
        title=network[1] or "HIDDEN NETWORK",
        back=f"/networks/{quote(city, safe='')}",
        **context,
    )
