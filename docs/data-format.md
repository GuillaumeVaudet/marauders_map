# Data format

This document describes the binary capture format (`.bin`, "MMAP"), how the
raw 802.11 frames are decoded, and the SQLite schema the data is stored in.

## 1. Capture file — MMAP binary format

### Overview

A capture file is a 5-byte header written once, followed by a sequence of
records concatenated with no separator. The file is read by streaming: each
record carries the length of its frame, so the reader always knows where the
next record begins.

```
┌───────────────────────────────┐
│  HEADER (5 bytes)             │   written once, at the start
├───────────────────────────────┤
│  RECORD 1                     │ ┐
│  RECORD 2                     │ │  repeated until EOF
│  ...                          │ ┘
└───────────────────────────────┘
```

Each record has a fixed-size metadata block followed by the raw frame:

```
┌──────────────────────┬───────────────────────────┐
│  METADATA (18 bytes) │  RAW FRAME (frame_len bytes) │
└──────────────────────┴───────────────────────────┘
```

All integers are **little-endian**.

### File header (5 bytes)

| Offset | Size | Field   | Meaning                                  |
| ------ | ---- | ------- | ---------------------------------------- |
| 0      | 4    | magic   | must equal `MMAP` (file type signature)  |
| 4      | 1    | version | format version (currently `1`), `uint8`  |

`struct` format: `<4sB`.

The reader rejects any file whose first 4 bytes are not `MMAP`.

### Metadata (18 bytes, fixed)

| Offset | Size | Field       | Type   | Meaning                                   |
| ------ | ---- | ----------- | ------ | ----------------------------------------- |
| 0      | 1    | node_id     | uint8  | capturing node (1–4)                      |
| 1      | 1    | rssi        | int8   | signal strength, negative (e.g. −82)      |
| 2      | 1    | channel     | uint8  | Wi-Fi channel (1–13)                      |
| 3      | 1    | band        | uint8  | 0 = 2.4 GHz, 1 = 5 GHz, 2 = BLE           |
| 4      | 4    | timestamp   | uint32 | Unix seconds UTC (0 = no GPS fix)         |
| 8      | 4    | latitude    | int32  | latitude ×1e7 (0 = no fix)                |
| 12     | 4    | longitude   | int32  | longitude ×1e7 (0 = no fix)               |
| 16     | 2    | frame_len   | uint16 | number of bytes of the frame that follows |

`struct` format: `<BbBBIiiH` (18 bytes).

### Coordinate and timestamp encoding

- **Coordinates** are stored as integers scaled by 1e7: the firmware takes the
  decimal degrees (e.g. `50.610752`) and multiplies by 1e7, which keeps an
  exact integer in 4 bytes and avoids floating-point imprecision. To read them
  back: `degrees = value / 1e7`. `int32` is signed to allow South/West
  (negative) coordinates.
- **Timestamp** is Unix epoch seconds. It is kept as an integer at storage
  time; conversion to a human date is done only at display time.
- A value of `0` for `timestamp`, `latitude` and `longitude` means **no GPS
  fix** (the firmware sets all three to 0 together). The reader converts these
  to `None` rather than treating `0` as a real value.

### Reading loop

```
open file
read and validate the 5-byte header
loop:
    read 18 bytes of metadata
    if nothing is returned -> end of file, stop
    decode frame_len from the metadata
    read frame_len bytes (the raw frame)
    yield the record
```

### Edge cases

- **Invalid header** (`magic != MMAP`): the reader raises an error.
- **Header only, 0 record**: valid, the reader yields nothing.
- **Truncated record**: planned behaviour — stop the analysis and offer a
  recovery tool that scans forward for the next valid header to resume
  decoding (see roadmap).

## 2. 802.11 frame decoding

The raw frame is an 802.11 **beacon** management frame. Fields are read at
fixed offsets in the MAC header, then from the Information Elements.

### MAC header

| Field               | Size | Offset |
| ------------------- | ---- | ------ |
| Frame Control       | 2    | 0–1    |
| Duration            | 2    | 2–3    |
| Address 1 (DA)      | 6    | 4–9    |
| Address 2 (SA)      | 6    | 10–15  |
| **Address 3 (BSSID)** | 6  | **16–21** |
| Sequence Control    | 2    | 22–23  |

The beacon body starts at offset 24: Timestamp (8) + Beacon Interval (2) +
Capability Info (2) = 12 fixed bytes, so the Information Elements begin at
**offset 36**.

### BSSID

The network identifier is Address 3, bytes 16–21, formatted as a MAC address:

```python
":".join(f"{b:02x}" for b in frame[16:22])
```

Some BSSIDs start with a byte whose "locally administered" bit is set (e.g.
`3a:07:16:...`) — these are **randomized MACs**, for which a vendor (OUI)
lookup returns nothing.

### SSID

The SSID is the first Information Element (tag 0) at offset 36:

- `frame[36]` = Element ID (0 for SSID)
- `frame[37]` = length (0–32)
- `frame[38 : 38 + length]` = the name (decoded UTF-8)

A length of 0 means a **hidden** SSID (or a secondary BSSID with no broadcast
name).

### Encryption

- Read Capability Info (2 bytes, little-endian) at offset 34:
  `struct.unpack_from("<H", frame, 34)[0]`.
- Isolate the **Privacy bit** (bit 4): `(capability >> 4) & 1`.
  - `0` → **OPEN** (no encryption).
- Otherwise parse the Information Elements:
  - IE **48** (RSN) present → **WPA2/WPA3**.
  - IE **221** with OUI `00:50:f2` type 1 → **WPA**.
  - else → **WEP**.

> WPA2 vs WPA3 are grouped: distinguishing them requires parsing the AKM
> suites inside the RSN element (planned).

## 3. Database schema

One SQLite database per city (`data/<city>.db`), with three tables. The design
separates the **network identity** from the **observations**, following the
model used by established wardriving tools.

### `network` — one row per BSSID (identity)

```sql
CREATE TABLE network (
    bssid TEXT PRIMARY KEY,
    ssid TEXT,
    encryption TEXT
)
```

### `record` — one row per observation (sighting)

```sql
CREATE TABLE record (
    id INTEGER PRIMARY KEY,
    bssid TEXT,
    node_id INTEGER,
    rssi INTEGER,
    channel INTEGER,
    band INTEGER,
    timestamp INTEGER,   -- nullable (no fix)
    latitude REAL,       -- nullable
    longitude REAL,      -- nullable
    frame_len INTEGER,
    frame BLOB           -- raw 802.11 frame, kept for re-decoding
)
```

### `imported_files` — import deduplication

```sql
CREATE TABLE imported_files (
    id INTEGER PRIMARY KEY,
    file_hash TEXT UNIQUE,
    file_name TEXT,
    imported_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### Relationships

`record.bssid` references `network.bssid`: a **one-to-many** relation (one
network, many observations). No junction table is needed — the foreign key is
the link. To list a network's observations: `SELECT ... FROM record WHERE
bssid = ?`. To combine both tables (e.g. observations with the network name):
a `JOIN` on `bssid`.

### Deduplication

- **Networks**: `bssid` is the PRIMARY KEY, so `INSERT OR IGNORE` keeps a
  single row per network even though it appears in thousands of captures.
- **Files**: before importing, the file's SHA-256 hash is compared against
  `imported_files`. An already-imported file is skipped. The whole import runs
  in a single transaction (one `commit` at the end), so a failure before commit
  leaves the database clean and the file can be re-imported.