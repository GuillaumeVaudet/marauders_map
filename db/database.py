import sqlite3

from models.metadata import Metadata

def connect(database_name: str) -> sqlite3.Connection:
    full_name = "data/" + database_name + ".db"
    connection = sqlite3.connect(full_name)
    return connection


def create_record_table(database_connection: sqlite3.Connection):
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
        )
    """)


def insert_record(database_connection: sqlite3.Connection, metadata: Metadata):
    database_connection.execute("""
        INSERT INTO record (node_id, rssi, channel, band, timestamp, 
        latitude, longitude, frame_len) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (metadata.node_id, metadata.rssi, metadata.channel, metadata.band, metadata.timestamp, 
          metadata.latitude, metadata.longitude, metadata.frame_len)
    )


if __name__ == "__main__":
    from core.reader import read_records
    from pathlib import Path

    city_name = "lille"
    test_path = Path("data_tests/capture_003.bin")

    connection = connect(city_name)
    create_record_table(connection)

    for metadata, frame in read_records(test_path):
        insert_record(connection, metadata)

    connection.commit()
    connection.close()