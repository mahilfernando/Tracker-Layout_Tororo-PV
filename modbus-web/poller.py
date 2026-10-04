"""Step 2: read the TBox every POLL_SECONDS and store everything in SQLite.

    python poller.py

Leave it running. It reconnects by itself if the TBox or network drops.

Tables in plant.db:
  readings         plant (ID 255) and Meteo 0 values, one row per tag per poll
  trackers_latest  newest state of every DBox (one row per tracker)
  tracker_history  every DBox every HISTORY_MINUTES (for charts)
  events           mode / alarm / position-code changes and plant alarms
"""

import sqlite3
import time
from datetime import datetime, timedelta, timezone

from pymodbus.exceptions import ModbusException

import config
import tbox_map as m
from modbus_io import make_client, read_block, read_global, read_meteo0

VERSION = config.TBOX_SYSTEM_VERSION
TRACKER_COLS = ["operation_mode", "setpoint", "position", "battery", "alarms",
                "motor_ma", "warnings", "position_code", "notifications"]


def open_db():
    db = sqlite3.connect(config.DB_PATH)
    db.execute("PRAGMA journal_mode=WAL")   # app.py can read while we write
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS readings (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            ts        TEXT    NOT NULL,          -- UTC, ISO 8601
            device_id INTEGER NOT NULL,          -- 255 = plant, 1-254 = block
            tag       TEXT    NOT NULL,
            value     REAL
        );
        CREATE INDEX IF NOT EXISTS ix_readings_tag_ts ON readings(device_id, tag, ts);

        CREATE TABLE IF NOT EXISTS trackers_latest (
            block INTEGER, dbox INTEGER, ts TEXT,
            operation_mode INTEGER, setpoint REAL, position REAL, battery REAL,
            alarms INTEGER, motor_ma INTEGER, warnings INTEGER,
            position_code INTEGER, notifications INTEGER,
            PRIMARY KEY (block, dbox)
        );

        CREATE TABLE IF NOT EXISTS tracker_history (
            ts TEXT, block INTEGER, dbox INTEGER,
            operation_mode INTEGER, setpoint REAL, position REAL, battery REAL,
            alarms INTEGER, position_code INTEGER
        );
        CREATE INDEX IF NOT EXISTS ix_hist ON tracker_history(block, dbox, ts);

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT, block INTEGER, dbox INTEGER,
            kind TEXT, severity TEXT, text TEXT
        );
        CREATE INDEX IF NOT EXISTS ix_events_ts ON events(ts);
        """
    )
    db.commit()
    return db


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- change detection -> events ---------------------------------------------

def tracker_events(old, new):
    """Compare two states of one DBox, return [(kind, severity, text)]."""
    ev = []
    if old["operation_mode"] != new["operation_mode"]:
        mode = new["operation_mode"]
        sev = "alarm" if mode in m.DEFECT_MODES else "info"
        ev.append(("mode", sev, f"Mode: {m.OPERATION_MODES.get(old['operation_mode'], old['operation_mode'])}"
                                f" → {m.OPERATION_MODES.get(mode, mode)}"))
    if old["alarms"] != new["alarms"]:
        before = set(m.decode_alarms(old["alarms"], VERSION))
        after = set(m.decode_alarms(new["alarms"], VERSION))
        for a in sorted(after - before):
            ev.append(("alarm", "alarm", f"Alarm ON: {a}"))
        for a in sorted(before - after):
            ev.append(("alarm", "clear", f"Alarm cleared: {a}"))
    if old["position_code"] != new["position_code"]:
        ev.append(("position", "info",
                   f"Position: {m.POSITION_CODES.get(old['position_code'], old['position_code'])}"
                   f" → {m.POSITION_CODES.get(new['position_code'], new['position_code'])}"))
    return ev


def plant_events(old, new):
    ev = []
    for tag in m.GLOBAL_ALARM_TAGS:
        if old and tag in old and old[tag] != new[tag]:
            on = bool(new[tag])
            sev = "info" if tag in ("BacktrackingStatus", "NightMode") else ("alarm" if on else "clear")
            ev.append(("plant", sev, f"{tag} {'ON' if on else 'OFF'}"))
    return ev


# --- main loop ---------------------------------------------------------------

def load_previous(db):
    prev = {}
    for row in db.execute(f"SELECT block, dbox, {', '.join(TRACKER_COLS)} FROM trackers_latest"):
        prev[(row[0], row[1])] = dict(zip(TRACKER_COLS, row[2:]))
    return prev


def prune(db):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=config.KEEP_DAYS)).isoformat(timespec="seconds")
    for table in ("readings", "tracker_history", "events"):
        db.execute(f"DELETE FROM {table} WHERE ts < ?", (cutoff,))
    db.commit()


def poll_once(client, db, prev_trackers, prev_plant, save_history):
    ts = now_iso()
    events = []
    readings = []

    # Plant status, ID 255
    try:
        plant = read_global(client)
        readings += [(ts, m.GLOBAL_UNIT_ID, k, v) for k, v in plant.items()]
        events += [(ts, m.GLOBAL_UNIT_ID, 0, *e) for e in plant_events(prev_plant, plant)]
        prev_plant.clear()
        prev_plant.update(plant)
    except (IOError, ModbusException) as e:
        print("plant read failed:", e)

    # Each power block
    ok_trackers = 0
    for block, count in config.BLOCKS.items():
        if config.READ_METEO0:
            try:
                meteo = read_meteo0(client, block)
                readings += [(ts, block, "Meteo0." + k, v) for k, v in meteo.items()]
            except (IOError, ModbusException) as e:
                print(f"block {block} meteo read failed:", e)
        try:
            rows = read_block(client, block, count)
        except (IOError, ModbusException) as e:
            print(f"block {block} read failed:", e)
            continue
        latest = []
        for r in rows:
            key = (block, r["dbox"])
            if key in prev_trackers:
                events += [(ts, block, r["dbox"], *e) for e in tracker_events(prev_trackers[key], r)]
            prev_trackers[key] = {c: r[c] for c in TRACKER_COLS}
            latest.append((block, r["dbox"], ts, *[r[c] for c in TRACKER_COLS]))
        db.executemany(
            f"INSERT OR REPLACE INTO trackers_latest (block, dbox, ts, {', '.join(TRACKER_COLS)}) "
            f"VALUES (?, ?, ?, {', '.join('?' * len(TRACKER_COLS))})",
            latest,
        )
        if save_history:
            db.executemany(
                "INSERT INTO tracker_history (ts, block, dbox, operation_mode, setpoint, position, "
                "battery, alarms, position_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(ts, r["block"], r["dbox"], r["operation_mode"], r["setpoint"], r["position"],
                  r["battery"], r["alarms"], r["position_code"]) for r in rows],
            )
        ok_trackers += len(rows)

    db.executemany("INSERT INTO readings (ts, device_id, tag, value) VALUES (?, ?, ?, ?)", readings)
    db.executemany("INSERT INTO events (ts, block, dbox, kind, severity, text) VALUES (?, ?, ?, ?, ?, ?)", events)
    db.commit()
    return ok_trackers, len(events)


def main():
    db = open_db()
    client = make_client()
    prev_trackers = load_previous(db)
    prev_plant = {}
    last_prune = None
    last_history = None
    total = sum(config.BLOCKS.values())
    print(f"Polling TBox {config.TBOX_IP}:{config.TBOX_PORT}, blocks {list(config.BLOCKS)} "
          f"({total} trackers) every {config.POLL_SECONDS}s -> {config.DB_PATH}")

    while True:
        started = time.monotonic()
        try:
            if not client.connected and not client.connect():
                raise ConnectionError("TBox not reachable")
            save_history = last_history is None or started - last_history >= config.HISTORY_MINUTES * 60
            n, n_ev = poll_once(client, db, prev_trackers, prev_plant, save_history)
            if save_history and n:
                last_history = started
            took = time.monotonic() - started
            print(f"{now_iso()}  {n}/{total} trackers read in {took:.1f}s, {n_ev} events")
            if took > config.POLL_SECONDS:
                print("  warning: a full read takes longer than POLL_SECONDS - increase it")
        except (ModbusException, ConnectionError, OSError) as e:
            print("read failed:", e)
            client.close()   # reconnect on the next loop

        if last_prune is None or time.monotonic() - last_prune > 24 * 3600:
            prune(db)
            last_prune = time.monotonic()

        time.sleep(max(0.0, config.POLL_SECONDS - (time.monotonic() - started)))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("stopped")
