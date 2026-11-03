// Map view: renders a downloaded PMTiles zone with the local night-city style.
(async function () {
  const container = document.getElementById("map");
  const TILTED_PITCH = 55;

  function showError(message) {
    const error = document.getElementById("map-error");
    error.textContent = message;
    error.hidden = false;
  }

  function kindOf(encryption) {
    return { OPEN: "open", WEP: "weak", WPA: "weak" }[encryption] || "secure";
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    node.className = className;
    node.textContent = text;
    return node;
  }

  // SSIDs are untrusted radio data: only ever insert them as text, never as HTML.
  function buildPopup(features) {
    const content = document.createElement("div");
    if (features.length > 1) {
      content.append(element("p", "popup-title", features.length + " networks at this position"));
    }
    const city = encodeURIComponent(container.dataset.city);
    for (const { properties: network } of features) {
      const row = element("article", "popup-network", "");
      row.append(
        element("p", network.ssid ? "popup-ssid" : "popup-ssid popup-ssid--hidden", network.ssid || "HIDDEN"),
        element("p", "popup-tag popup-tag--" + network.kind, network.encryption),
        element(
          "p",
          "popup-data",
          `${network.rssi} dBm · ${network.observations} observation${network.observations > 1 ? "s" : ""}`
        )
      );
      const link = element("a", "popup-link", network.bssid);
      link.href = "/networks/" + city + "/" + encodeURIComponent(network.bssid);
      row.append(link);
      content.append(row);
    }
    return content;
  }

  function addNetworkLayers(map) {
    map.addSource("networks", {
      type: "geojson",
      data: { type: "FeatureCollection", features: [] },
      cluster: true,
      clusterMaxZoom: 14,
      clusterRadius: 38,
    });
    map.addLayer({
      id: "network-clusters",
      type: "circle",
      source: "networks",
      filter: ["has", "point_count"],
      paint: {
        "circle-color": "#06070c",
        "circle-opacity": 0.9,
        "circle-stroke-color": "#f1e6df",
        "circle-stroke-width": 1.5,
        "circle-radius": ["step", ["get", "point_count"], 13, 25, 17, 100, 22, 500, 28],
      },
    });
    map.addLayer({
      id: "network-cluster-counts",
      type: "symbol",
      source: "networks",
      filter: ["has", "point_count"],
      layout: {
        "text-field": ["get", "point_count_abbreviated"],
        "text-font": ["Noto Sans Medium"],
        "text-size": 12,
        "text-allow-overlap": true,
      },
      paint: { "text-color": "#f1e6df" },
    });
    map.addLayer({
      id: "network-points",
      type: "circle",
      source: "networks",
      filter: ["!", ["has", "point_count"]],
      paint: {
        "circle-color": ["match", ["get", "kind"], "open", "#f8297f", "weak", "#cf7a10", "#00a6ae"],
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 12, 4, 18, 8],
        "circle-stroke-color": "#06070c",
        "circle-stroke-width": 2,
      },
    });
  }

  function enablePopups(map) {
    const popup = new maplibregl.Popup({
      closeOnClick: false,
      maxWidth: "320px",
      className: "network-popup",
    });
    let pinned = false;
    popup.on("close", () => {
      pinned = false;
    });

    function networksAround(point) {
      const features = map.queryRenderedFeatures(
        [[point.x - 5, point.y - 5], [point.x + 5, point.y + 5]],
        { layers: ["network-points"] }
      );
      // A point can be returned once per tile.
      return [...new Map(features.map((feature) => [feature.properties.bssid, feature])).values()];
    }

    function showPopup(event) {
      const features = networksAround(event.point);
      if (features.length > 0) {
        popup
          .setLngLat(features[0].geometry.coordinates)
          .setDOMContent(buildPopup(features))
          .addTo(map);
      }
    }

    map.on("mouseenter", "network-points", (event) => {
      map.getCanvas().style.cursor = "pointer";
      if (!pinned) {
        showPopup(event);
      }
    });
    map.on("mouseleave", "network-points", () => {
      map.getCanvas().style.cursor = "";
      if (!pinned) {
        popup.remove();
      }
    });
    map.on("click", "network-points", (event) => {
      showPopup(event);
      pinned = true;
    });
    map.on("click", (event) => {
      if (pinned && networksAround(event.point).length === 0) {
        popup.remove();
      }
    });

    map.on("mouseenter", "network-clusters", () => {
      map.getCanvas().style.cursor = "pointer";
    });
    map.on("mouseleave", "network-clusters", () => {
      map.getCanvas().style.cursor = "";
    });
    map.on("click", "network-clusters", async (event) => {
      const [cluster] = map.queryRenderedFeatures(event.point, { layers: ["network-clusters"] });
      const zoom = await map
        .getSource("networks")
        .getClusterExpansionZoom(cluster.properties.cluster_id);
      map.easeTo({ center: cluster.geometry.coordinates, zoom });
    });
  }

  function enableLegend(map, features) {
    const legend = document.getElementById("map-legend");
    const checkboxes = [...legend.querySelectorAll("input[data-kind]")];
    const total = document.getElementById("map-network-count");

    for (const { dataset } of legend.querySelectorAll("[data-count]")) {
      const count = features.filter((feature) => feature.properties.kind === dataset.count).length;
      legend.querySelector(`[data-count="${dataset.count}"]`).textContent = count;
    }

    function applyFilter() {
      const visibleKinds = checkboxes.filter((box) => box.checked).map((box) => box.dataset.kind);
      const visible = features.filter((feature) => visibleKinds.includes(feature.properties.kind));
      // Filtering the data, not the layer, so that the clusters count visible networks only.
      map.getSource("networks").setData({ type: "FeatureCollection", features: visible });
      total.textContent = visible.length;
    }

    legend.addEventListener("change", applyFilter);
    applyFilter();
    legend.hidden = false;
  }

  async function loadNetworks(map) {
    const response = await fetch(container.dataset.networks);
    if (!response.ok) {
      throw new Error("this database has no network data yet");
    }
    const { features } = await response.json();
    for (const feature of features) {
      feature.properties.kind = kindOf(feature.properties.encryption);
    }

    addNetworkLayers(map);
    enablePopups(map);
    enableLegend(map, features);

    if (features.length > 0) {
      const bounds = new maplibregl.LngLatBounds();
      features.forEach((feature) => bounds.extend(feature.geometry.coordinates));
      map.fitBounds(bounds, { padding: 70, maxZoom: 15, duration: 0 });
    }
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

    if (container.dataset.networks) {
      map.once("load", () => {
        loadNetworks(map).catch((error) => {
          showError("Networks could not be loaded: " + error.message);
        });
      });
    }
  }

  try {
    await start();
  } catch (error) {
    showError("Map could not be loaded: " + error.message);
  }
})();
