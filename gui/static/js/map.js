// Map view: renders a downloaded PMTiles zone with the local night-city style.
(async function () {
  const container = document.getElementById("map");
  const TILTED_PITCH = 55;

  function showError(message) {
    const error = document.getElementById("map-error");
    error.textContent = message;
    error.hidden = false;
  }

  async function start() {
    const tilesUrl = location.origin + container.dataset.tiles;
    const protocol = new pmtiles.Protocol();
    maplibregl.addProtocol("pmtiles", protocol.tile);

    const archive = new pmtiles.PMTiles(tilesUrl);
    protocol.add(archive);
    const header = await archive.getHeader();

    const response = await fetch("/static/map/style.json");
    const style = await response.json();
    style.sources.protomaps.url = "pmtiles://" + tilesUrl;
    style.glyphs = location.origin + "/static/map/fonts/{fontstack}/{range}.pbf";

    const zoneBounds = [
      [header.minLon, header.minLat],
      [header.maxLon, header.maxLat],
    ];
    const fitOptions = { padding: 24, pitch: 0, bearing: 0 };

    const map = new maplibregl.Map({
      container,
      style,
      bounds: zoneBounds,
      fitBoundsOptions: { padding: 24 },
      maxBounds: [
        [header.minLon - 0.15, header.minLat - 0.1],
        [header.maxLon + 0.15, header.maxLat + 0.1],
      ],
      minZoom: 8,
      maxZoom: 19,
      maxPitch: 70,
      attributionControl: { compact: false },
    });
    map.getCanvas().focus();

    const tiltButton = document.getElementById("map-tilt");

    // Follows the real pitch, which also changes with right drag or animations.
    map.on("pitch", () => {
      tiltButton.setAttribute("aria-pressed", String(map.getPitch() >= 1));
    });

    document.getElementById("map-zoom-in").addEventListener("click", () => map.zoomIn());
    document.getElementById("map-zoom-out").addEventListener("click", () => map.zoomOut());
    document.getElementById("map-reset").addEventListener("click", () => {
      map.fitBounds(zoneBounds, fitOptions);
    });
    tiltButton.addEventListener("click", () => {
      map.easeTo({ pitch: map.getPitch() < 1 ? TILTED_PITCH : 0 });
    });

    const latitude = document.getElementById("map-latitude");
    const longitude = document.getElementById("map-longitude");
    const zoom = document.getElementById("map-zoom");

    function updatePosition(position) {
      latitude.textContent = position.lat.toFixed(5);
      longitude.textContent = position.lng.toFixed(5);
    }

    function updateZoom() {
      zoom.textContent = map.getZoom().toFixed(1);
    }

    map.on("mousemove", (event) => updatePosition(event.lngLat));
    map.on("move", updateZoom);
    updatePosition(map.getCenter());
    updateZoom();
  }

  try {
    await start();
  } catch (error) {
    showError("Map could not be loaded: " + error.message);
  }
})();
