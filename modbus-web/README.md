# Modbus TCP → local database → web dashboard

Reads values from a Modbus TCP device (tracker PLC, inverter, meter…), stores them
in a local SQLite file, and shows them on a web page that any PC on the plant
network can open.

```
Device ──Modbus TCP:502──▶ poller.py ──▶ plant.db ──▶ app.py ──HTTP:8000──▶ browser
                          (pymodbus)    (SQLite)    (FastAPI)
```

| File | What it does |
|---|---|
| `config.py` | **The only file you normally edit**: device IP, unit id, register map |
| `read_test.py` | Step 1: connect once and print every tag |
| `poller.py` | Step 2: read every 5 s, save to `plant.db`, reconnect on errors |
| `app.py` | Step 3: web API (`/api/latest`, `/api/history/{tag}`, `/api/tags`, `/docs`) |
| `static/index.html` | Step 4: dashboard (live tiles + history chart, no internet needed) |
| `simulator.py` | Fake tracker for testing without hardware |

## 1. Install (once)

Python 3.10 or newer (from python.org, not the Microsoft Store).

> **Windows:** keep the folder at a short path with no spaces or `&`, for
> example `C:\tracker\modbus-web`. Long paths (over 260 characters inside the
> venv) and `&` make `python -m venv` fail with
> `ensurepip ... returned non-zero exit status 1`.

```bash
cd modbus-web
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
```

## 2. Try it with the simulator first (no hardware)

Three terminals, each with the venv activated, in the `modbus-web` folder:

```bash
python simulator.py                                   # terminal 1: fake device on port 5020
```
```bash
set MODBUS_IP=127.0.0.1& set MODBUS_PORT=5020& python poller.py     # terminal 2 (Windows cmd)
# PowerShell:  $env:MODBUS_IP="127.0.0.1"; $env:MODBUS_PORT="5020"; python poller.py
# Linux/Mac:   MODBUS_IP=127.0.0.1 MODBUS_PORT=5020 python poller.py
```
```bash
uvicorn app:app --host 0.0.0.0 --port 8000            # terminal 3
```

Open http://localhost:8000.

## 3. Connect your real device

1. Put the device and the PC on the same subnet and check `ping <device IP>`.
2. In `config.py` set `DEVICE_IP`, `UNIT_ID` and the `TAGS` register map from the
   device manual:
   - The manual's register **40001** is `address: 0` in code (40011 → 10).
   - Function 03 = `"kind": "holding"`, function 04 = `"kind": "input"`.
   - Values that can be negative (angles) need `"signed": True`.
   - `scale` turns the raw integer into real units (raw 325 × 0.1 = 32.5°).
3. If you're unsure of the map, check it with a free tool such as QModMaster first.
4. `python read_test.py` and compare the numbers with the device's own display.
5. Run `poller.py` and `uvicorn app:app --host 0.0.0.0 --port 8000` as above (without the `MODBUS_*` variables).

Other PCs open `http://<this PC's IP>:8000`. Allow inbound TCP port 8000 in
Windows Firewall.

## Notes

- **Read only.** This project never writes registers. Writing to a tracker
  controller moves real equipment; add that only deliberately.
- **Database.** Table `readings(ts, device_id, tag, value)`, one row per tag per
  poll, timestamps in UTC. Rows older than `KEEP_DAYS` are deleted daily. Open
  `plant.db` with "DB Browser for SQLite" to inspect it.
- **32-bit values** (energy counters, floats) span two registers; they need an
  extra decode step that this version doesn't do yet.
- **Run on boot.** On Windows use NSSM or Task Scheduler for `poller.py` and
  uvicorn; on Linux use systemd units.
- **Security.** Keep it on the plant LAN. Add a login before exposing it anywhere else.
