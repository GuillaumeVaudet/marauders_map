import os
import signal

from fastapi import APIRouter, Request
from starlette.background import BackgroundTask

from db.database import list_databases
from gui.common import render

router = APIRouter()


def stop_server() -> None:
    os.kill(os.getpid(), signal.SIGINT)


@router.get("/")
def main_menu(request: Request):
    return render(request, "main_menu.html", databases=list_databases())


@router.get("/settings")
def settings(request: Request):
    return render(
        request,
        "message.html",
        section="SETTINGS",
        title="SETTINGS",
        message="No settings available yet.",
        back="/",
    )


@router.post("/quit")
def quit_application(request: Request):
    response = render(
        request,
        "message.html",
        section="OFFLINE",
        title="SESSION CLOSED",
        message="The server has stopped. You can close this tab.",
        push_url="/",
        offline=True,
    )
    response.background = BackgroundTask(stop_server)
    return response
