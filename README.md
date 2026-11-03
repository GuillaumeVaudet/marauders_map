# maraudeurs_map

Local tool that aggregates wardriving captures. It imports `.bin` capture files
(MMAP format) into one SQLite database per city, then lets you browse the WiFi
networks and their observations from a terminal (TUI) or a browser (GUI).

Everything runs locally. The GUI has no login and only listens on `127.0.0.1`.

## Installation

Tested with Python 3.15.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p data/maps
```

Run all commands from the project root: the `data/` folder is a relative path.

## Usage

```bash
.venv/bin/python -m gui       # browser: http://127.0.0.1:8000 (--port to change)
.venv/bin/python main.py      # terminal
```

Both interfaces offer the same features:

- **Networks**: list of detected networks and the observations of each one.
- **Statistics**: totals and encryption breakdown for a database.
- **Data Manager**: import a capture, create a database, view imported files,
  delete one database or all of them.

To add a capture, open **Data Manager > Import file**, select the file and enter
the city name. The database `data/<city>.db` is created if it does not exist, and
a file that was already imported is ignored.

The browser also has a **Map** view. It does not show the networks yet.

## Map

Each map zone is one `.pmtiles` file in `data/maps/`, which works offline once
downloaded. Install the
[`pmtiles` tool](https://github.com/protomaps/go-pmtiles/releases), pick a recent
build date from the
[list of builds](https://build-metadata.protomaps.dev/builds.json), then extract
a zone with `--bbox=<west>,<south>,<east>,<north>`.

For example, the Lille metropolitan area (about 56 MB):

```bash
pmtiles extract https://build.protomaps.com/YYYYMMDD.pmtiles data/maps/mel.pmtiles \
  --bbox=2.76,50.48,3.30,50.81 --maxzoom=15
```

The file name becomes the zone name, and each file in the folder appears in the
Map view. The look of the map is defined in `gui/static/map/style.json`.

Map data: © [OpenStreetMap](https://openstreetmap.org/copyright) contributors,
through [Protomaps](https://protomaps.com).

## Project layout

```text
core/    capture file reader and frame decoder
models/  data classes
db/      SQLite access and import logic
tui/     terminal interface (Textual)
gui/     browser interface (FastAPI, HTMX, MapLibre)
data/    databases and map zones, not versioned
```

### TODO:
    [ ] save network trames
    [ ] Manufacturer enrichment via YES lookup / BLE Company ID;
    [ ] Multi-nodes handling
    [ ] 5Ghz and BLE
    [ ] Statistics
    [ ] Exports
