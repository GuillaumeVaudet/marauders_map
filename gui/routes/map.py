from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from db.database import list_databases
from gui.common import open_database, render

MAPS_DIRECTORY = Path("data/maps")

# Each network is placed at its strongest observation with a GPS position.
# With MAX(), SQLite takes the other selected columns from the row holding the maximum.
NETWORK_POSITIONS_QUERY = """
    SELECT network.bssid, network.ssid, network.encryption,
           strongest.rssi, strongest.latitude, strongest.longitude,
           strongest.observations
    FROM network
    JOIN (
        SELECT bssid, MAX(rssi) AS rssi, latitude, longitude,
               COUNT(*) AS observations
        FROM record
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        GROUP BY bssid
    ) AS strongest ON strongest.bssid = network.bssid
"""

router = APIRouter(prefix="/map")


def list_zones() -> list[str]:
    return sorted(path.stem for path in MAPS_DIRECTORY.glob("*.pmtiles"))


@router.get("")
def map_view(request: Request, zone: str = "", database: str = ""):
    zones = list_zones()
    if not zones:
        return render(
            request,
            "message.html",
            active="map",
            section="MAP",
            title="NO MAP ZONE",
            message="No map zone has been downloaded yet.",
            hint="See the Map section of the README to download one into data/maps.",
            back="/",
        )

    databases = sorted(list_databases(), key=str.casefold)
    selected_database = database if database in databases else next(iter(databases), None)
    return render(
        request,
        "map.html",
        active="map",
        section="MAP",
        title=(zone if zone in zones else zones[0]),
        zones=zones,
        databases=databases,
        database=selected_database,
        back="/",
    )


@router.get("/networks/{city}")
def network_positions(city: str):
    with open_database(city) as connection:
        rows = connection.execute(NETWORK_POSITIONS_QUERY).fetchall()

    return JSONResponse({
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                "properties": {
                    "bssid": bssid,
                    "ssid": ssid,
                    "encryption": encryption,
                    "rssi": rssi,
                    "observations": observations,
                },
            }
            for bssid, ssid, encryption, rssi, latitude, longitude, observations in rows
        ],
    })
