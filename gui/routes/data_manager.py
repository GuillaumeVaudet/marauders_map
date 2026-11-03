from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Form, HTTPException, Request

from db.database import (
    connect,
    create_imported_file_table,
    create_record_table,
    delete_all_databases,
    delete_database,
    get_imported_files,
    import_file,
    list_databases,
)
from gui.common import (
    Toast,
    is_valid_new_name,
    open_database,
    render,
    require_database,
)

router = APIRouter(prefix="/data-manager")


def show_menu(request: Request, toast: Toast | None = None, push_url: str | None = None):
    return render(
        request,
        "data_manager.html",
        active="data-manager",
        section="DATA MANAGER",
        title="DATA MANAGER",
        back="/",
        toast=toast,
        push_url=push_url,
    )


def resolve_inside_project(raw_path: str) -> Path:
    """Limit the file browser to the launch folder, like the TUI DirectoryTree."""
    root = Path.cwd().resolve()
    path = (root / raw_path).resolve()
    if not path.is_relative_to(root):
        raise HTTPException(404, "Path not found")
    return path


def list_directory(directory: Path) -> tuple[list[Path], list[Path]]:
    try:
        entries = sorted(directory.iterdir(), key=lambda entry: entry.name.casefold())
    except OSError:
        return [], []
    return (
        [entry for entry in entries if entry.is_dir()],
        [entry for entry in entries if entry.is_file()],
    )


def show_import_dialog(request: Request, path: Path, toast: Toast | None = None):
    root = Path.cwd().resolve()
    return render(
        request,
        "import_dialog.html",
        active="data-manager",
        section="DATA MANAGER // IMPORT FILE",
        title="IMPORT FILE",
        back="/data-manager/import?path="
        + quote(str(path.parent.relative_to(root)), safe=""),
        file_name=path.name,
        relative_path=str(path.relative_to(root)),
        databases=list_databases(),
        toast=toast,
    )


def show_create_dialog(request: Request, toast: Toast | None = None):
    return render(
        request,
        "create_dialog.html",
        active="data-manager",
        section="DATA MANAGER // CREATE DATABASE",
        title="CREATE DATABASE",
        back="/data-manager",
        toast=toast,
    )


@router.get("")
def data_manager(request: Request):
    return show_menu(request)


@router.get("/import")
def file_browser(request: Request, path: str = "."):
    directory = resolve_inside_project(path)
    if not directory.is_dir():
        raise HTTPException(404, "Folder not found")

    root = Path.cwd().resolve()
    folders, files = list_directory(directory)
    return render(
        request,
        "file_browser.html",
        active="data-manager",
        section="DATA MANAGER // IMPORT FILE",
        title="SELECT CAPTURE",
        back="/data-manager",
        current=str(directory.relative_to(root)),
        parent=None if directory == root else str(directory.parent.relative_to(root)),
        folders=[str(folder.relative_to(root)) for folder in folders],
        files=[
            (str(file.relative_to(root)), file.stat().st_size)
            for file in files
        ],
    )


@router.get("/import/file")
def import_dialog(request: Request, path: str):
    file_path = resolve_inside_project(path)
    if not file_path.is_file():
        raise HTTPException(404, "File not found")
    return show_import_dialog(request, file_path)


@router.post("/import")
def import_capture(request: Request, path: str = Form(), city: str = Form("")):
    file_path = resolve_inside_project(path)
    if not file_path.is_file():
        raise HTTPException(404, "File not found")

    city = city.strip()
    if not city:
        toast = Toast("Please enter a city name", "warning")
        return show_import_dialog(request, file_path, toast)
    if not is_valid_new_name(city):
        toast = Toast(f"Invalid city name: {city}", "warning")
        return show_import_dialog(request, file_path, toast)

    try:
        imported = import_file(file_path, city)
    except Exception as error:
        # Any file can be selected, and the decoder raises various errors on
        # data that is not a valid capture: report them instead of crashing.
        toast = Toast(f"Import failed: {file_path.name} ({error})", "error")
        return show_import_dialog(request, file_path, toast)

    if imported:
        toast = Toast(f"Imported: {file_path.name} into {city}")
    else:
        toast = Toast(f"Already imported: {file_path.name}", "warning")
    return show_menu(request, toast, push_url="/data-manager")


@router.get("/create")
def create_dialog(request: Request):
    return show_create_dialog(request)


@router.post("/create")
def create_database(request: Request, city: str = Form("")):
    city = city.strip()
    if not city:
        return show_create_dialog(request, Toast("Please enter a city name", "warning"))
    if not is_valid_new_name(city):
        return show_create_dialog(request, Toast(f"Invalid city name: {city}", "warning"))
    if Path(f"data/{city}.db").exists():
        return show_create_dialog(
            request, Toast(f"Database '{city}' already exists", "warning")
        )

    connection = connect(city)
    create_record_table(connection)
    create_imported_file_table(connection)
    connection.commit()
    connection.close()
    return show_menu(request, Toast(f"Database created: {city}"), push_url="/data-manager")


@router.get("/imported")
def select_imported_database(request: Request):
    return render(
        request,
        "select_database.html",
        active="data-manager",
        section="DATA MANAGER // IMPORTED FILES",
        title="IMPORTED FILES",
        databases=list_databases(),
        base_url="/data-manager/imported",
        back="/data-manager",
    )


@router.get("/imported/{city}")
def imported_files(request: Request, city: str):
    with open_database(city) as connection:
        files = get_imported_files(connection)
    return render(
        request,
        "imported_files.html",
        active="data-manager",
        section=f"DATA MANAGER // IMPORTED FILES // {city}",
        title=city,
        back="/data-manager/imported",
        files=files,
    )


@router.get("/delete")
def select_database_to_delete(request: Request):
    return render(
        request,
        "select_database.html",
        active="data-manager",
        section="DATA MANAGER // DELETE DATABASE",
        title="DELETE DATABASE",
        databases=list_databases(),
        base_url="/data-manager/delete",
        back="/data-manager",
        danger=True,
    )


@router.get("/delete/{city}")
def confirm_delete(request: Request, city: str):
    require_database(city)
    return render(
        request,
        "confirm_dialog.html",
        active="data-manager",
        section="DATA MANAGER // DELETE DATABASE",
        title="DELETE DATABASE",
        back="/data-manager/delete",
        message=f"Delete database '{city}' ?",
        action=f"/data-manager/delete/{quote(city, safe='')}",
        confirm_label="Yes, delete",
    )


@router.post("/delete/{city}")
def delete_city_database(request: Request, city: str):
    require_database(city)
    delete_database(city)
    return show_menu(request, Toast(f"Database deleted: {city}"), push_url="/data-manager")


@router.get("/delete-all")
def confirm_delete_all(request: Request):
    return render(
        request,
        "confirm_dialog.html",
        active="data-manager",
        section="DATA MANAGER // DELETE ALL",
        title="DELETE ALL",
        back="/data-manager",
        message="Delete ALL databases? This cannot be undone.",
        action="/data-manager/delete-all",
        confirm_label="Yes, delete all",
    )


@router.post("/delete-all")
def delete_all(request: Request):
    count = delete_all_databases()
    return show_menu(request, Toast(f"{count} database(s) deleted"), push_url="/data-manager")
