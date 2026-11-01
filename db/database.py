from pathlib import Path
import sqlite3
from sqlite3 import Connection
import hashlib

from models.metadata import Metadata
from core.reader import read_records


def list_databases():
    return [path.stem for path in Path("data").glob("*.db")]


def get_imported_files(database_connection: Connection):
    cursor = database_connection.execute(
        "SELECT file_name, imported_at FROM imported_files "
        "ORDER BY imported_at"
    )
    return cursor.fetchall()

def delete_database(city: str) -> bool:
    path = Path(f"data/{city}.db")
    if path.exists():
        path.unlink()
        return True
    return False


def delete_all_databases() -> int:
    paths = list(Path("data").glob("*.db"))
    for path in paths:
        path.unlink()
    return len(paths)


def compute_file_hash(path: str):
    hasher = hashlib.sha256()
    with open(path, 'rb') as file:
        while True:
            bloc = file.read(65536)
            if not bloc:
                break    
            hasher.update(bloc)
    return hasher.hexdigest()


def create_imported_file_table(database_connection: Connection):
    database_connection.execute("""
        CREATE TABLE IF NOT EXISTS imported_files (
            id INTEGER PRIMARY KEY,
            file_hash TEXT UNIQUE,
            file_name TEXT,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


def is_already_imported(database_connection: Connection, file_hash) -> bool:
    cursor = database_connection.execute(
        "SELECT 1 FROM imported_files WHERE file_hash = ?",
        (file_hash,)
    )
    result = cursor.fetchone()

    return result is not None


def mark_as_imported(database_connection: Connection, file_hash, file_name):
    database_connection.execute(
        "INSERT INTO imported_files (file_hash, file_name) VALUES (?, ?)",
        (file_hash, file_name)
    )


def connect(database_name: str) -> Connection:
    full_name = "data/" + database_name + ".db"
    connection = sqlite3.connect(full_name)
    return connection


def create_record_table(database_connection: Connection):
    database_connection.execute("""
        CREATE TABLE IF NOT EXISTS record (
            id INTEGER PRIMARY KEY,
            node_id INTEGER,
            rssi INTEGER,
            channel INTEGER,
            band INTEGER,
            timestamp INTEGER,
            latitude REAL,
            longitude REAL,
            frame_len INTEGER
            frame BLOB
        )
    """)


def insert_record(database_connection: Connection, metadata: Metadata):
    database_connection.execute("""
        INSERT INTO record (node_id, rssi, channel, band, timestamp, 
        latitude, longitude, frame_len) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (metadata.node_id, metadata.rssi, metadata.channel, metadata.band, metadata.timestamp, 
          metadata.latitude, metadata.longitude, metadata.frame_len)
    )


def import_file(path, city):
    file_hash = compute_file_hash(path)
    connection = connect(city)

    create_record_table(connection)
    create_imported_file_table(connection)

    if is_already_imported(connection, file_hash):
        print("File was already imported, please select another one")
        connection.close()
        return False
    
    for metadata, frame in read_records(path):
        insert_record(connection, metadata)

    mark_as_imported(connection, file_hash, path.name)
    connection.commit()
    connection.close()
    return True

if __name__ == "__main__":

    city_name = "lille"
    test_path = Path("data_tests/capture_003.bin")

    import_file(test_path, city_name)