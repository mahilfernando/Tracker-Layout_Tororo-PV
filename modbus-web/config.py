"""Settings shared by read_test.py, poller.py and app.py.

Edit this file to match your device. Everything else reads from here.
"""

import os
from pathlib import Path

# --- Modbus TCP device -------------------------------------------------------
# MODBUS_IP / MODBUS_PORT environment variables override these (handy for the simulator).
DEVICE_IP = os.environ.get("MODBUS_IP", "192.168.1.50")        # [YOUR DEVICE IP]
DEVICE_PORT = int(os.environ.get("MODBUS_PORT", "502"))         # standard Modbus TCP port
UNIT_ID = 1                  # unit / slave id from the device manual
POLL_SECONDS = 5             # how often poller.py reads the device

# --- Register map ------------------------------------------------------------
# One entry per value you want to log. Fill these in from the device manual.
#   address : register number used in code (manual "40001" -> 0, "40011" -> 10)
#   kind    : "holding" (function 03) or "input" (function 04)
#   signed  : True for int16 values that can be negative (angles, power flow)
#   scale   : multiply the raw integer by this to get real units
TAGS = [
    {"name": "tracker_angle_deg", "address": 0, "kind": "holding", "signed": True,  "scale": 0.1,  "unit": "°"},
    {"name": "target_angle_deg",  "address": 1, "kind": "holding", "signed": True,  "scale": 0.1,  "unit": "°"},
    {"name": "motor_current_a",   "address": 2, "kind": "holding", "signed": False, "scale": 0.01, "unit": "A"},
    {"name": "status_code",       "address": 3, "kind": "holding", "signed": False, "scale": 1,    "unit": ""},
]

# --- Local database ----------------------------------------------------------
DB_PATH = Path(__file__).parent / "plant.db"   # SQLite file, created automatically
KEEP_DAYS = 90               # older rows are deleted once a day
