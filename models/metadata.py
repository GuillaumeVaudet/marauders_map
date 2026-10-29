from dataclasses import dataclass

@dataclass
class Metadata:
    node_id: int
    rssi: int
    channel: int
    band: int
    timestamp: int
    latitude: int
    longitude: int
    frame_len: int