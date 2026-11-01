import struct


def decode_bssid(frame: bytes) -> str:
    return ":".join(f"{byte:02x}" for byte in frame[16:22])


def decode_ssid(frame: bytes) -> str:
    ssid_length = frame[37]
    return frame[38:38 + ssid_length].decode("utf-8", errors="replace")


def parse_information_elements(frame: bytes, start: int = 36) -> dict:
    elements = {}
    index = start
    while index + 2 <= len(frame):
        element_id = frame[index]
        length = frame[index + 1]
        elements[element_id] = frame[index + 2:index + 2 + length]
        index += 2 + length
    return elements


def decode_encryption(frame: bytes) -> str:
    capability = struct.unpack_from("<H", frame, 34)[0]
    privacy = (capability >> 4) & 1
    if not privacy:
        return "OPEN"

    elements = parse_information_elements(frame)
    if 48 in elements:
        return "WPA2/WPA3"
    if 221 in elements and elements[221][:4] == b"\x00\x50\xf2\x01":
        return "WPA"
    return "WEP"


if __name__ == "__main__":
    from core.reader import read_records

    count = 0
    for metadata, frame in read_records("data_tests/capture_003.bin"):
        print("---- BSSID ----")
        print(decode_bssid(frame))
        print("---- SSID ----")
        print(decode_ssid(frame))
        print("---- encryption ----")
        print(decode_encryption(frame))
        count += 1
        if count >= 50:
            break