"""Step 2: read the device every few seconds and store the values in SQLite.

    python poller.py

Leave it running. It reconnects by itself if the device or network drops.
"""

import sqlite3
import time
from datetime import datetime, timedelta, timezone

from pymodbus.exceptions import ModbusException

import config
from modbus_io import make_client, read_tags


def open_db():
    db = sqlite3.connect(config.DB_PATH)
    db.execute("PRAGMA journal_mode=WAL")  # lets app.py read while we write
    db.execute(
        """CREATE TABLE IF NOT EXISTS readings (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            ts        TEXT    NOT NULL,   -- UTC, ISO 8601
            device_id INTEGER NOT NULL,
            tag       TEXT    NOT NULL,
            value     REAL
        )"""
    )
    db.execute("CREATE INDEX IF NOT EXISTS ix_tag_ts ON readings(tag, ts)")
    db.commit()
    return db


def prune(db):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=config.KEEP_DAYS)).isoformat(timespec="seconds")
    db.execute("DELETE FROM readings WHERE ts < ?", (cutoff,))
    db.commit()


def main():
    db = open_db()
    client = make_client()
    last_prune = 0.0
    print(f"Polling {config.DEVICE_IP}:{config.DEVICE_PORT} every {config.POLL_SECONDS}s -> {config.DB_PATH}")

    while True:
        started = time.monotonic()
        try:
            if not client.connected and not client.connect():
                raise ConnectionError("device not reachable")
            values = read_tags(client)
            ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
            db.executemany(
                "INSERT INTO readings (ts, device_id, tag, value) VALUES (?, ?, ?, ?)",
                [(ts, config.UNIT_ID, name, value) for name, value in values.items()],
            )
            db.commit()
            print(ts, values)
        except (ModbusException, ConnectionError, IOError) as e:
            print("read failed:", e)
            client.close()  # reconnect on the next loop

        if time.monotonic() - last_prune > 24 * 3600:
            prune(db)
            last_prune = time.monotonic()

        time.sleep(max(0.0, config.POLL_SECONDS - (time.monotonic() - started)))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("stopped")
