from dataclasses import dataclass

@dataclass
class Metadata:
    node_id: int
    rssi: int
    channel: int
    band: int
    timestamp: int | None
    latitude: int | None
    longitude: int | None
    frame_len: int