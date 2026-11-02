from dataclasses import dataclass


@dataclass
class Network:
    bssid: str
    ssid: str
    encryption: str