"""Step 1: connect once, print every tag, exit.

    python read_test.py
"""

import config
from modbus_io import make_client, read_tags

client = make_client()
if not client.connect():
    raise SystemExit(
        f"Cannot reach {config.DEVICE_IP}:{config.DEVICE_PORT} - "
        "check the IP, the cable, and that this PC is on the same subnet."
    )

try:
    for name, value in read_tags(client).items():
        print(f"{name:20} {value}")
finally:
    client.close()
