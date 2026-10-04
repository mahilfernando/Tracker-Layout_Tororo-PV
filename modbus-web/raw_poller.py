"""Test mode: read any block of registers from any Modbus TCP device, show
them in the terminal, store them in plant.db, and serve them on the
dashboard's "Raw test" page (http://localhost:8000/raw.html).

    python raw_poller.py --ip 192.168.1.21 --unit 1 --start 45000 --count 20

--start accepts either the manual style (45000 / 405000 / 35000) or the
plain offset (5000). Manual style is converted: 4xxxx -> holding register
xxxx, 3xxxx -> input register xxxx.

Read-only: it never writes to the device.
"""

import argparse
import sqlite3
import time
from datetime import datetime, timezone

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

import config


def parse_start(text, force_input, one_based=False):
    """Return (kind, wire_address, label) from 45000, 405000, 35000, 5000...

    one_based=False (PVH manual): 40000 is register 0, so 45000 -> wire 5000.
    one_based=True (Modbus Poll / most tools): 40001 is register 0, so
    45000 -> wire 4999.
    """
    n = int(text)
    shift = 1 if one_based else 0
    for lo, hi, base, kind in ((400000, 465536, 400000, "holding"), (300000, 365536, 300000, "input"),
                               (40000, 49999, 40000, "holding"), (30000, 39999, 30000, "input")):
        if lo <= n <= hi:
            if n - base - shift < 0:
                raise SystemExit(f"With --one-based the first register is {base + 1}, not {n}.")
            return kind, n - base - shift, n
    kind = "input" if force_input else "holding"
    return kind, n, n + (30000 if kind == "input" else 40000) + shift


def to_signed(v):
    return v - 65536 if v > 32767 else v


def open_db():
    db = sqlite3.connect(config.DB_PATH)
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS raw_latest (
            address INTEGER PRIMARY KEY,   -- manual-style address, e.g. 45000
            ts TEXT, source TEXT, value INTEGER
        );
        CREATE TABLE IF NOT EXISTS raw_history (
            ts TEXT, address INTEGER, value INTEGER
        );
        CREATE INDEX IF NOT EXISTS ix_raw_hist ON raw_history(address, ts);
        """
    )
    db.commit()
    return db


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ip", default=config.TBOX_IP)
    ap.add_argument("--port", type=int, default=config.TBOX_PORT)
    ap.add_argument("--unit", type=int, default=1, help="unit / slave / device id")
    ap.add_argument("--start", default="45000", help="first register, e.g. 45000 or 5000")
    ap.add_argument("--count", type=int, default=20, help="how many registers (1-125)")
    ap.add_argument("--input", action="store_true", help="read input registers (function 04) for a plain offset")
    ap.add_argument("--every", type=float, default=5, help="seconds between reads")
    ap.add_argument("--once", action="store_true", help="read once and exit (no database)")
    ap.add_argument("--one-based", action="store_true",
                    help="45000 means wire address 4999 (Modbus Poll style) instead of 5000 (PVH manual style)")
    args = ap.parse_args()

    kind, wire, label = parse_start(args.start, args.input, args.one_based)
    count = max(1, min(args.count, 125))
    fc = 3 if kind == "holding" else 4
    source = f"{args.ip}:{args.port} unit {args.unit} FC{fc:02d}"
    print(f"Reading {count} {kind} registers from {source}, "
          f"{label}..{label + count - 1} (wire address {wire}..{wire + count - 1})")

    client = ModbusTcpClient(args.ip, port=args.port, timeout=3)
    db = None if args.once else open_db()
    db_clear = True

    while True:
        started = time.monotonic()
        try:
            if not client.connected and not client.connect():
                raise ConnectionError(f"cannot reach {args.ip}:{args.port}")
            read = client.read_holding_registers if kind == "holding" else client.read_input_registers
            rr = read(wire, count=count, device_id=args.unit)
            if rr.isError():
                raise IOError(f"device answered with an error: {rr}")
            ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

            print(f"\n{ts}   {'address':>8} {'uint16':>7} {'int16':>7}  hex")
            for i, v in enumerate(rr.registers):
                print(f"{'':25} {label + i:>8} {v:>7} {to_signed(v):>7}  0x{v:04X}")

            if db is not None:
                if db_clear:   # new test run: forget addresses from an older run
                    db.execute("DELETE FROM raw_latest")
                    db_clear = False
                rows = [(label + i, ts, source, v) for i, v in enumerate(rr.registers)]
                db.executemany("INSERT OR REPLACE INTO raw_latest (address, ts, source, value) VALUES (?, ?, ?, ?)", rows)
                db.executemany("INSERT INTO raw_history (ts, address, value) VALUES (?, ?, ?)",
                               [(ts, a, v) for a, _t, _s, v in rows])
                db.commit()
        except (ModbusException, ConnectionError, OSError) as e:
            print("read failed:", e)
            client.close()

        if args.once:
            break
        time.sleep(max(0.0, args.every - (time.monotonic() - started)))
    client.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("stopped")
