"""Step 3: web API + dashboard on top of plant.db.

    uvicorn app:app --host 0.0.0.0 --port 8000

Then open http://localhost:8000 (or http://<this PC's IP>:8000 from another PC).
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

import config
import tbox_map as m

HERE = Path(__file__).parent
VERSION = config.TBOX_SYSTEM_VERSION
PLANT_UNITS = {name: unit for name, _o, _s, _sc, unit in m.GLOBAL_TAGS}

app = FastAPI(title="Tororo PV tracker monitor")


def query(sql, args=()):
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(sql, args)]
    except sqlite3.OperationalError:
        return []  # tables not created yet: poller.py has not run
    finally:
        con.close()


def decorate(row):
    """Add human-readable text to a tracker row."""
    row["mode_text"] = m.OPERATION_MODES.get(row["operation_mode"], f"Unknown ({row['operation_mode']})")
    row["position_text"] = m.POSITION_CODES.get(row["position_code"], f"Unknown ({row['position_code']})")
    row["alarm_list"] = m.decode_alarms(row["alarms"] or 0, VERSION)
    row["outdated"] = m.is_outdated(row, VERSION)
    row["defect"] = row["operation_mode"] in m.DEFECT_MODES
    row["deviation"] = round(row["position"] - row["setpoint"], 2)
    return row


@app.get("/api/meta")
def meta():
    return {"blocks": config.BLOCKS, "version": VERSION, "poll_seconds": config.POLL_SECONDS,
            "operation_modes": m.OPERATION_MODES, "position_codes": m.POSITION_CODES}


@app.get("/api/plant")
def plant():
    """Newest plant-wide values (ID 255) and Meteo 0 of each block."""
    rows = query("SELECT device_id, tag, value, MAX(ts) AS ts FROM readings GROUP BY device_id, tag")
    out = {"plant": {}, "meteo": {}, "ts": None}
    for r in rows:
        if r["device_id"] == m.GLOBAL_UNIT_ID:
            out["plant"][r["tag"]] = r["value"]
            out["ts"] = max(out["ts"] or "", r["ts"])
        elif r["tag"].startswith("Meteo0."):
            out["meteo"].setdefault(str(r["device_id"]), {})[r["tag"][7:]] = r["value"]
    out["units"] = PLANT_UNITS
    return out


@app.get("/api/summary")
def summary():
    """Counts per block for the overview cards."""
    rows = [decorate(r) for r in query("SELECT * FROM trackers_latest")]
    blocks = {}
    for b, expected in config.BLOCKS.items():
        blocks[b] = {"block": b, "expected": expected, "read": 0, "auto": 0, "alarm": 0,
                     "defect": 0, "outdated": 0, "ts": None}
    for r in rows:
        s = blocks.setdefault(r["block"], {"block": r["block"], "expected": 0, "read": 0, "auto": 0,
                                           "alarm": 0, "defect": 0, "outdated": 0, "ts": None})
        s["read"] += 1
        s["auto"] += r["operation_mode"] == 1
        s["alarm"] += bool(r["alarms"])
        s["defect"] += r["defect"]
        s["outdated"] += r["outdated"]
        s["ts"] = max(s["ts"] or "", r["ts"])
    return list(blocks.values())


@app.get("/api/trackers")
def trackers(block: int):
    rows = query("SELECT * FROM trackers_latest WHERE block = ? ORDER BY dbox", (block,))
    return [decorate(r) for r in rows]


@app.get("/api/tracker/{block}/{dbox}")
def tracker(block: int, dbox: int, hours: float = 24):
    latest = query("SELECT * FROM trackers_latest WHERE block = ? AND dbox = ?", (block, dbox))
    if not latest:
        raise HTTPException(404, f"no data for block {block} DBox {dbox}")
    since = (datetime.now(timezone.utc) - timedelta(hours=max(0.1, min(hours, 24 * 31)))).isoformat(timespec="seconds")
    history = query(
        "SELECT ts, setpoint, position, operation_mode, alarms, battery FROM tracker_history "
        "WHERE block = ? AND dbox = ? AND ts >= ? ORDER BY ts", (block, dbox, since))
    events = query("SELECT ts, kind, severity, text FROM events WHERE block = ? AND dbox = ? "
                   "ORDER BY id DESC LIMIT 50", (block, dbox))
    return {"latest": decorate(latest[0]), "history": history, "events": events}


@app.get("/api/plant/history/{tag}")
def plant_history(tag: str, hours: float = 24):
    if tag not in PLANT_UNITS:
        raise HTTPException(404, f"unknown tag {tag}")
    since = (datetime.now(timezone.utc) - timedelta(hours=max(0.1, min(hours, 24 * 31)))).isoformat(timespec="seconds")
    return query("SELECT ts, value FROM readings WHERE device_id = ? AND tag = ? AND ts >= ? ORDER BY ts",
                 (m.GLOBAL_UNIT_ID, tag, since))


@app.get("/api/events")
def events(limit: int = 100, block: int | None = None):
    limit = max(1, min(limit, 1000))
    if block is None:
        return query("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))
    return query("SELECT * FROM events WHERE block = ? ORDER BY id DESC LIMIT ?", (block, limit))


# Must come last: serves static/index.html at "/"
app.mount("/", StaticFiles(directory=HERE / "static", html=True), name="static")
