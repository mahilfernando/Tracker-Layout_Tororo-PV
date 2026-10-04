"""Step 3: web API + dashboard on top of plant.db.

    uvicorn app:app --host 0.0.0.0 --port 8000

Then open http://localhost:8000 (or http://<this PC's IP>:8000 from another PC).
"""

import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

import config

HERE = Path(__file__).parent
TAG_NAMES = {t["name"] for t in config.TAGS}

app = FastAPI(title="Tracker monitor")


def query(sql, args=()):
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(sql, args)]
    except sqlite3.OperationalError:
        return []  # table not created yet: poller.py has not run
    finally:
        con.close()


@app.get("/api/tags")
def tags():
    """The register map, so the page knows names and units."""
    return config.TAGS


@app.get("/api/latest")
def latest():
    """Newest value of every tag (SQLite returns the row holding MAX(ts))."""
    return query("SELECT tag, value, MAX(ts) AS ts FROM readings GROUP BY tag")


@app.get("/api/history/{tag}")
def history(tag: str, limit: int = 720):
    """Last `limit` readings of one tag, oldest first (720 x 5 s = 1 hour)."""
    if tag not in TAG_NAMES:
        raise HTTPException(404, f"unknown tag {tag}")
    limit = max(1, min(limit, 20000))
    rows = query(
        "SELECT ts, value FROM readings WHERE tag = ? ORDER BY ts DESC LIMIT ?",
        (tag, limit),
    )
    return rows[::-1]


# Must come last: serves static/index.html at "/"
app.mount("/", StaticFiles(directory=HERE / "static", html=True), name="static")
