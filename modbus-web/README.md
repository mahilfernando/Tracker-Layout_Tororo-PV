# Tororo PV tracker monitor: PVH TBox (Modbus TCP) → local database → web dashboard

Reads the PVH DeepTrack **TBox** over Modbus TCP (server port 502), stores the
data in a local SQLite file, and shows it on a web page that any PC on the
plant network can open. **Read-only:** it never writes registers, so it cannot
move trackers.

```
TBox ──Modbus TCP:502──▶ poller.py ──▶ plant.db ──▶ app.py ──HTTP:8000──▶ browser
                        (pymodbus)    (SQLite)    (FastAPI)
```

What it reads (per manual PVH-RD-DC-MAN-0020-01_A10):

| Modbus ID | What | Registers |
|---|---|---|
| 255 | Plant status: time, sun, auto target, backtracking, night mode, wind, UPS, snow, diffuse, hail | 40000–40038 |
| 1–254 (one per power block) | Meteo 0: wind 3 s / 30 s, battery, alarms | 40020–40029 |
| 1–254 | Each DBox (tracker): operation mode, setpoint, position, battery, alarm bits, motor current, warnings, position code, notifications | 40050–48049, 16 per DBox |

The manual's address 4xxxx is sent on the wire as xxxx (40011 → 11), as the
manual's "HOLDING REGISTER" column shows. Everything is read with function 03,
in requests of 80 registers, as the manual recommends.

| File | What it does |
|---|---|
| `config.py` | **The only file you normally edit**: TBox IP, list of blocks and DBox counts |
| `tbox_map.py` | The TBox register map and decode tables (modes, alarm bits, position codes) |
| `read_test.py` | Step 1: connect once, print plant status and the first trackers of each block |
| `poller.py` | Step 2: read every 10 s, save to `plant.db`, log mode and alarm changes as events |
| `app.py` | Step 3: web API (`/api/plant`, `/api/summary`, `/api/trackers?block=1`, `/api/tracker/1/7`, `/api/events`, `/docs`) |
| `static/index.html` | Step 4: dashboard (plant cards, block overview, tracker table with filters, tracker history, event log) |
| `simulator.py` | Fake TBox for testing without the plant |
| `setup.bat` | Windows: double-click once to create `venv` and install libraries |
| `demo.bat` | Windows: starts simulator + poller + web server and opens the dashboard |
| `raw_poller.py`, `raw.bat`, `static/raw.html` | Test mode: read any N registers from any device and show them |
| `find_tbox.py`, `find_tbox.bat` | Scan the network for Modbus devices and spot the TBox |
| `run.bat` | Windows: starts poller + web server for the real TBox in `config.py` |

## 1. Install (once)

Python 3.10 or newer (from python.org, not the Microsoft Store). Tick
**"Add python.exe to PATH"** in the installer.

> **Windows:** keep the folder at a short path with no spaces or `&`, for
> example `C:\tracker\modbus-web`. Long paths (over 260 characters inside the
> venv) and `&` make `python -m venv` fail with
> `ensurepip ... returned non-zero exit status 1`.

Double-click `setup.bat`, or by hand:

```bat
cd /d C:\tracker\modbus-web
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Try it with the simulator (no plant needed)

Double-click `demo.bat`. It opens three windows (simulator, poller, web
server) and the dashboard at http://localhost:8000. The simulator serves the
blocks in `config.py`, a 10-minute "day", and a few faulty trackers (block 1
DBox 3 and 7, and the last DBox of the last block).

## Quick test on any Modbus device (raw mode)

Reads a block of registers from any device and shows them at
http://localhost:8000/raw.html (uint16, int16, hex, ÷10, ÷100, and a chart per register).

Edit the four lines at the top of `raw.bat` (IP, UNIT, START, COUNT) and
double-click it. Or run it by hand:

```bat
venv\Scripts\python raw_poller.py --ip 192.168.1.21 --unit 1 --start 45000 --count 20
venv\Scripts\python raw_poller.py --ip 192.168.1.21 --unit 1 --start 45000 --count 20 --once
```

`--start` takes 45000 / 405000 (holding), 35000 (input, function 04), or a
plain offset like 5000. By default 45000 is sent as wire address 5000, like the
PVH manual (40000 = register 0). Add `--one-based` to match Modbus Poll and
similar tools, where 45000 is wire address 4999. `raw.bat` uses `--one-based`.

## 3. Connect to the real TBox

Don't know the TBox IP? Double-click `find_tbox.bat`. It scans 192.168.1.x for
Modbus devices and flags the one that answers on ID 255 with a date and time.

1. Put this PC on the TBox network and check `ping <TBox IP>`.
2. In `config.py` set:
   - `TBOX_IP`: the TBox address.
   - `BLOCKS`: `{block Modbus ID: number of DBoxes}` for every power block, from the commissioning team.
   - `TBOX_SYSTEM_VERSION`: `"3.2"` or `"3.1"`. It changes the meaning of alarm bit 15.
3. Run `venv\Scripts\python read_test.py` and compare the positions with the PVH app.
4. Double-click `run.bat`.

Other PCs open `http://<this PC's IP>:8000`. Allow inbound TCP port 8000 in
Windows Firewall.

## Load on the TBox

One poll reads ID 255 (1 request), Meteo 0 (1 request per block) and the
DBoxes (about 1 request per 5 DBoxes). A 500-DBox block is 100 requests. At
the manual's ~8 ms per request, that is about 1 s per block. The poller
prints how long each cycle takes and warns if it exceeds `POLL_SECONDS`. If
another SCADA also polls the TBox, use the manual's section 5 to choose a
safe period.

## Database (`plant.db`)

- `trackers_latest`: newest state of every tracker.
- `tracker_history`: every tracker every `HISTORY_MINUTES` (default 5).
- `events`: mode changes, alarms on/off, position-code changes, plant alarms.
- `readings`: plant (ID 255) and Meteo 0 values on every poll.

Rows older than `KEEP_DAYS` (default 30) are deleted daily. Open the file with
"DB Browser for SQLite" to inspect it.

## Not read yet

Gateway, Tracknet, Meteo 1–5, flood zones and the wired sensor converters
(48050–48784). On TBox 5 and later, wind data lives in the sensor converter
section, so plant wind speed may read 0 there. Ask and it can be added.
