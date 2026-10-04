"""PVH DeepTrack TBox Modbus map (server port 502), from manual
PVH-RD-DC-MAN-0020-01_A10.

All values are holding registers (function 03). The manual writes addresses
as 4xxxx; the number sent on the wire is that minus 40000
(manual 40011 -> address 11), as its "HOLDING REGISTER" column shows.

Each entry: (name, offset, signed, scale, unit). The real value is
raw / scale, e.g. ElevationPosition raw 3000 with scale 100 -> 30.00 degrees.
"""

# --- ID 255: General TBox map, GLOBAL STATUS (40000-40038) -------------------
GLOBAL_UNIT_ID = 255
GLOBAL_START = 0
GLOBAL_TAGS = [
    ("YearUTC", 0, False, 1, ""),
    ("MonthUTC", 1, False, 1, ""),
    ("DayUTC", 2, False, 1, ""),
    ("HourUTC", 3, False, 1, ""),
    ("MinuteUTC", 4, False, 1, ""),
    ("SecondUTC", 5, False, 1, ""),
    ("SunAzimuth", 6, False, 100, "°"),
    ("SunZenith", 7, True, 100, "°"),
    ("SunAngle", 8, True, 100, "°"),
    ("GlobalAutoElevationTarget", 9, True, 100, "°"),
    ("GlobalWindDirectionEW", 10, False, 1, ""),      # 1 East, 2 West
    ("BacktrackingStatus", 11, False, 1, ""),
    ("NightSetpoint", 12, True, 100, "°"),
    ("NightMode", 13, False, 1, ""),
    ("WindDirection", 14, False, 1, "°"),             # TBox 3.1
    ("WindSpeed", 15, False, 100, "m/s"),             # TBox 3.1
    ("WindAlarm", 16, False, 1, ""),
    ("WindInactivityAlarm", 17, False, 1, ""),
    ("UpsAlarm", 18, False, 1, ""),
    ("UpsBattery", 19, False, 1, ""),                 # 1 = TBox running on UPS
    ("UpsCharging", 20, False, 1, ""),
    ("AnemometerActiveNumber", 21, False, 1, ""),
    ("AnemometerTotalNumber", 22, False, 1, ""),
    ("AnemometerWarning", 23, False, 1, ""),
    ("SnowState", 24, False, 1, ""),
    ("InternalSnowSensorValue", 25, False, 1, "cm"),
    ("ApplicableSnowSensorValue", 26, False, 1, "cm"),
    ("DiffuseState", 27, False, 1, ""),
    ("InternalDiffuseSensorValue", 28, False, 100, "%"),
    ("ApplicableDiffuseSensorValue", 29, False, 100, "%"),
    ("HailState", 30, False, 1, ""),                  # 0 ok, 1 alarmed, 2 counting down
    ("InternalHailSensorValue", 31, False, 1, ""),
    ("ApplicableHailSensorValue", 32, False, 1, ""),
    ("PredictiveHailAlarm", 33, False, 1, ""),        # 32767 = no data
    ("PredictiveHeartbeat", 34, False, 1, ""),
    ("PredictiveDataValidTimeout", 35, False, 1, ""),
    ("HailingDataSource", 36, False, 1, ""),
    ("HailStowDirection", 37, False, 1, ""),
    ("FuotaState", 38, False, 1, ""),
]
GLOBAL_COUNT = 39

# Global 0/1 flags that raise an event when they change
GLOBAL_ALARM_TAGS = ["WindAlarm", "WindInactivityAlarm", "UpsAlarm", "UpsBattery",
                     "AnemometerWarning", "BacktrackingStatus", "NightMode"]

# --- ID 1-254: METEO 0 of each power block (40020-40029) ---------------------
METEO0_START = 20
METEO0_TAGS = [
    ("WindSpeed3s", 20, False, 100, "m/s"),
    ("WindDirection3s", 21, False, 1, "°"),
    ("WindSpeed30s", 22, False, 100, "m/s"),
    ("WindDirection30s", 23, False, 1, "°"),
    ("BatteryLevel", 24, False, 100, "%"),
    ("Alarms", 25, False, 1, ""),                     # bit0 anemometer, bit1 charger
    ("Ew3s", 26, False, 1, ""),
    ("Ew30s", 27, False, 1, ""),
    ("Notifications", 28, False, 1, ""),              # bit0 outdated
    ("WindSpeedEffective", 29, False, 100, "m/s"),
]
METEO0_COUNT = 10

# --- ID 1-254: DBox 1-500 (40050-48049), 16 registers per DBox --------------
DBOX_FIRST = 50
DBOX_STRIDE = 16
DBOX_USED = 11            # offsets 0-10 used, 11-15 spare
MAX_DBOX = 500

# (field, offset in the DBox slot, signed, scale)
DBOX_FIELDS = [
    ("control_word", 0, False, 1),      # RW - never written by this app
    ("manual_target", 1, True, 100),    # RW - never written by this app
    ("operation_mode", 2, False, 1),
    ("setpoint", 3, True, 100),
    ("position", 4, True, 100),
    ("battery", 5, False, 100),
    ("alarms", 6, False, 1),
    ("motor_ma", 7, False, 1),
    ("warnings", 8, False, 1),
    ("position_code", 9, False, 1),
    ("notifications", 10, False, 1),
]


def dbox_address(n):
    """Wire address of the first register of DBox n (1-based)."""
    return DBOX_FIRST + DBOX_STRIDE * (n - 1)


# --- Decode tables (Single Tracker Register Description) ---------------------
OPERATION_MODES = {
    0: "Defect: not recognized",
    1: "Auto (TBox control)",
    2: "Remote: manual position",
    3: "Local: PVH application",
    4: "Halt: waiting for acknowledge",
    5: "Remote: manual wind position",
    6: "Defect: secure battery",
    7: "Defect: fault stop",
    8: "Local: emergency stop",
    9: "Remote: manual stop",
    10: "Defect: TBox comms lost",
    11: "Local: buttons",
    12: "Remote: manual construction position",
}
DEFECT_MODES = {0, 4, 6, 7, 8, 10}

POSITION_CODES = {
    0: "Tracking",
    1: "Night position",
    2: "Backtracking",
    3: "Diffuse",
    4: "Reserved",
    5: "Wind defense",
    6: "Construction defense",
    7: "Snow position",
    8: "Hail position",
    9: "User position",
    10: "Stop position",
}

ALARM_BITS = {
    "3.2": [
        "Emergency stop", "Charger fault", "Inclinometer fault",
        "Wrong direction movement", "Overcurrent fault", "Slow motor movement",
        "High power consumption", "Static inclinometer read", "Out of boundaries",
        "Low battery", "Low temperature", "High temperature", "PV panel fault",
        "Wrong firmware fault", "Angle step fault", "Maximum movement time",
    ],
    "3.1": [
        "Emergency stop button pressed", "Charger fault", "Inclinometer fault",
        "Motor wrong direction fault", "Motor overcurrent", "Slow motor",
        "High power consumption", "Static inclinometer read", "Angle out of boundaries",
        "Low battery", "Low temperature", "High temperature", "PV panel voltage fault",
        "Wrong FW fault", "Angle step fault", "Outdated DBox data",
    ],
}


def decode_alarms(word, version="3.2"):
    names = ALARM_BITS.get(version, ALARM_BITS["3.2"])
    return [names[b] for b in range(16) if word >> b & 1]


def is_outdated(row, version="3.2"):
    """DBox data is stale: Notifications bit 0 (3.2) or Alarms bit 15 (3.1)."""
    if version == "3.1":
        return bool(row["alarms"] >> 15 & 1)
    return bool(row["notifications"] & 1)
