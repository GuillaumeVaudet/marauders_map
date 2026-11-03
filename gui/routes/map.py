from pathlib import Path

from fastapi import APIRouter, Request

from gui.common import render

MAPS_DIRECTORY = Path("data/maps")

router = APIRouter(prefix="/map")


def list_zones() -> list[str]:
    return sorted(path.stem for path in MAPS_DIRECTORY.glob("*.pmtiles"))


@router.get("")
def map_view(request: Request, zone: str = ""):
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

    return render(
        request,
        "map.html",
        active="map",
        section="MAP",
        title=(zone if zone in zones else zones[0]),
        zones=zones,
        back="/",
    )
