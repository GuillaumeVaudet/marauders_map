"""
Reader service.

Contains logic to read MMAP files.
"""
import struct
from pathlib import Path

from models.metadata import Metadata

def read_header(target_file):
    """Check header of the open target file 'target_file and return version"""
    header = target_file.read(5)

    if header[:4] != b"MMAP":
        raise ValueError("It's not an MMAP file")
    return header[4]


def decode_metadata(data) -> Metadata:
    """decode given metadata and return a Metadata"""
    return Metadata(*struct.unpack("<BbBBIiiH", data))


def read_records(path: str | Path):
    """Open the 'path' file and read it's content"""
    with open(path, 'rb') as file:
        version = read_header(file)
        while True:
            meta_bytes = file.read(18)
            if not meta_bytes:
                break
            metadata = decode_metadata(meta_bytes)
            frame = file.read(metadata.frame_len)
            yield (metadata, frame)


if __name__ == "__main__":
    number_of_records = 0

    # Ici phase de test sinon en prod récupération du path par la sélection 
    # dans le GUI/TUI
    test_path = Path("data_tests/capture_003.bin")
    for record in read_records(test_path):
        number_of_records += 1
    print(number_of_records)
