"""Step 1: connect once to the TBox, print plant status and the first trackers, exit.

    python read_test.py
"""

import config
import tbox_map as m
from modbus_io import make_client, read_block, read_global

client = make_client()
if not client.connect():
    raise SystemExit(
        f"Cannot reach TBox at {config.TBOX_IP}:{config.TBOX_PORT} - "
        "check the IP, the cable, and that this PC is on the same subnet."
    )

try:
    print(f"--- Plant status (Modbus ID {m.GLOBAL_UNIT_ID}) ---")
    try:
        for name, value in read_global(client).items():
            print(f"  {name:30} {value}")
    except IOError as e:
        print("  could not read:", e)

    for block, count in config.BLOCKS.items():
        print(f"\n--- Block {block}: first {min(count, 5)} of {count} DBoxes ---")
        try:
            for r in read_block(client, block, min(count, 5)):
                mode = m.OPERATION_MODES.get(r["operation_mode"], r["operation_mode"])
                alarms = ", ".join(m.decode_alarms(r["alarms"], config.TBOX_SYSTEM_VERSION)) or "none"
                print(f"  DBox {r['dbox']:3}  pos {r['position']:7.2f}°  setpoint {r['setpoint']:7.2f}°  "
                      f"battery {r['battery']:6.2f}%  mode: {mode}  alarms: {alarms}")
        except IOError as e:
            print("  could not read:", e)
finally:
    client.close()
