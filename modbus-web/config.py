"""Settings shared by read_test.py, poller.py, app.py and simulator.py.

Edit this file to match your plant. Everything else reads from here.
"""

import os
from pathlib import Path

# --- TBox connection (Modbus TCP) --------------------------------------------
# MODBUS_IP / MODBUS_PORT environment variables override these (used by demo.bat).
TBOX_IP = os.environ.get("MODBUS_IP", "192.168.1.50")    # [YOUR TBOX IP]
TBOX_PORT = int(os.environ.get("MODBUS_PORT", "502"))     # TBox server port 502
TIMEOUT_S = 3

# --- Power blocks to read ----------------------------------------------------
# {Modbus ID (= block number): number of DBoxes (trackers) in that block}
# Ask the commissioning team for the real list, e.g. {1: 412, 2: 398, 3: 405}.
# If the TBox renumbers blocks above 254 (manual section 4), use the Modbus ID.
BLOCKS = {
    1: 20,    # [FILL IN]
    2: 20,    # [FILL IN]
}

# TBox system version: "3.2" or "3.1" (changes the meaning of alarm bit 15)
TBOX_SYSTEM_VERSION = "3.2"

# --- Polling -----------------------------------------------------------------
POLL_SECONDS = 10       # one full read of the plant every 10 s
REQUEST_SIZE = 80       # registers per request, as the manual recommends
READ_METEO0 = True      # also read Meteo 0 (wind) of each block

# --- Local database ----------------------------------------------------------
DB_PATH = Path(__file__).parent / "plant.db"   # SQLite file, created automatically
HISTORY_MINUTES = 5     # tracker positions are saved to history every 5 min
KEEP_DAYS = 30          # older history / events are deleted once a day
