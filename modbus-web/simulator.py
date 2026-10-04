"""A fake Modbus TCP tracker for testing without real hardware.

    python simulator.py            # listens on 127.0.0.1:5020

Then set DEVICE_IP = "127.0.0.1" and DEVICE_PORT = 5020 in config.py.

It answers function 03 (holding) and 04 (input) reads. Registers 0-3 follow
config.TAGS: the angle sweeps -55..+55 degrees and back, like a tracker over
a (very fast) day. Written in plain asyncio so it does not depend on any
library version.
"""

import asyncio
import math
import struct
import time

HOST, PORT = "127.0.0.1", 5020
registers = [0] * 100


def update_registers():
    t = time.time()
    target = 55 * math.sin(t / 60 * math.pi)        # one sweep per minute
    actual = target - 0.3 * math.cos(t)              # lags a little
    moving = abs(actual - target) > 0.2
    registers[0] = int(round(actual * 10)) & 0xFFFF  # int16, x0.1
    registers[1] = int(round(target * 10)) & 0xFFFF
    registers[2] = int(84 if moving else 3)          # x0.01 A
    registers[3] = 0                                 # 0 = tracking OK


async def handle(reader, writer):
    try:
        while True:
            header = await reader.readexactly(7)
            tid, pid, length, unit = struct.unpack(">HHHB", header)
            pdu = await reader.readexactly(length - 1)
            fc = pdu[0]
            if fc in (3, 4) and len(pdu) == 5:
                addr, count = struct.unpack(">HH", pdu[1:5])
                if 1 <= count <= 125 and addr + count <= len(registers):
                    update_registers()
                    data = struct.pack(f">{count}H", *registers[addr:addr + count])
                    body = bytes([fc, len(data)]) + data
                else:
                    body = bytes([fc | 0x80, 2])             # illegal address
            else:
                body = bytes([fc | 0x80, 1])                 # illegal function
            writer.write(struct.pack(">HHHB", tid, pid, len(body) + 1, unit) + body)
            await writer.drain()
    except (asyncio.IncompleteReadError, ConnectionResetError):
        pass
    finally:
        writer.close()


async def main():
    server = await asyncio.start_server(handle, HOST, PORT)
    print(f"Simulated tracker on {HOST}:{PORT} (Ctrl+C to stop)")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
