"""A fake PVH TBox (Modbus TCP) for testing without the real plant.

    python simulator.py            # listens on 127.0.0.1:5020

Then run the poller with MODBUS_IP=127.0.0.1 and MODBUS_PORT=5020 (demo.bat
does this for you). It serves ID 255 (plant status) and every block listed in
config.BLOCKS, laid out exactly like the TBox map: DBox n at 50 + 16*(n-1).

A "day" lasts 10 minutes so you can watch trackers move. A few trackers have
faults so the alarm list and event log have something to show:
  block 1 DBox 3  - low battery alarm that comes and goes every 2 minutes
  block 1 DBox 7  - inclinometer fault, mode "Defect: fault stop"
  last block, last DBox - outdated data (no news from the DBox)

Plain asyncio, function 03 only, no library needed.
"""

import asyncio
import math
import random
import struct
import time

import config
import tbox_map as m

HOST, PORT = "127.0.0.1", 5020
DAY_SECONDS = 600


def u16(v):
    return int(round(v)) & 0xFFFF


def global_registers(t):
    regs = [0] * 200
    now = time.gmtime(t)
    phase = (t % DAY_SECONDS) / DAY_SECONDS            # 0..1 over the fake day
    sun = 90 - 180 * phase                              # +90 (east) .. -90 (west)
    target = max(-55, min(55, sun)) if 0.1 < phase < 0.9 else 0
    wind = 4 + 3 * math.sin(t / 37) + random.random()
    regs[0:6] = [now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec]
    regs[6] = u16((90 + 180 * phase) * 100)
    regs[7] = u16((90 - abs(sun)) * 100)
    regs[8] = u16(sun * 100)
    regs[9] = u16(target * 100)
    regs[10] = 1 if sun > 0 else 2
    regs[11] = 1 if 0.1 < phase < 0.2 or 0.8 < phase < 0.9 else 0
    regs[12] = 0
    regs[13] = 0 if 0.1 < phase < 0.9 else 1
    regs[14] = int(t / 5) % 360
    regs[15] = u16(wind * 100)
    regs[16] = 1 if wind > 7.5 else 0
    regs[21], regs[22] = 2, 2
    regs[33] = 0
    regs[36] = 2
    regs[37] = 1
    return regs, target


def block_registers(block, count, t, target):
    regs = [0] * (m.dbox_address(m.MAX_DBOX) + m.DBOX_STRIDE)
    wind = 4 + 3 * math.sin(t / 37)
    regs[20:30] = [u16(wind * 100), 270, u16(wind * 100), 265, 9500, 0, 2, 2, 0, u16(wind * 80)]
    last_block = list(config.BLOCKS)[-1]
    for n in range(1, count + 1):
        a = m.dbox_address(n)
        lag = 0.3 * math.sin(t / 7 + n)                 # trackers lag a little
        mode, pos_code, alarms, notif = 1, 0, 0, 0
        position = target + lag
        battery = 80 + (n * 7) % 20
        if target == 0:
            pos_code = 1                                 # night position
        if block == 1 and n == 3 and int(t / 120) % 2:
            alarms |= 1 << 9                             # low battery
            battery = 12
        if block == 1 and n == 7:
            mode, pos_code, position = 7, 10, 12.4       # fault stop, stuck
            alarms |= 1 << 2                             # inclinometer fault
        if block == last_block and n == count:
            notif = 1                                    # outdated
        regs[a + 0] = 0
        regs[a + 1] = 0
        regs[a + 2] = mode
        regs[a + 3] = u16(target * 100)
        regs[a + 4] = u16(position * 100)
        regs[a + 5] = u16(battery * 100)
        regs[a + 6] = alarms
        regs[a + 7] = 1800 + (n * 37) % 400
        regs[a + 8] = 64
        regs[a + 9] = pos_code
        regs[a + 10] = notif
    return regs


def registers_for(unit):
    t = time.time()
    glob, target = global_registers(t)
    if unit == m.GLOBAL_UNIT_ID:
        return glob
    if unit in config.BLOCKS:
        return block_registers(unit, config.BLOCKS[unit], t, target)
    return None


async def handle(reader, writer):
    try:
        while True:
            header = await reader.readexactly(7)
            tid, pid, length, unit = struct.unpack(">HHHB", header)
            pdu = await reader.readexactly(length - 1)
            fc = pdu[0]
            regs = registers_for(unit)
            if regs is None:
                body = bytes([fc | 0x80, 0x0B])              # no such ID
            elif fc == 3 and len(pdu) == 5:
                addr, count = struct.unpack(">HH", pdu[1:5])
                if 1 <= count <= 125 and addr + count <= len(regs):
                    data = struct.pack(f">{count}H", *regs[addr:addr + count])
                    body = bytes([fc, len(data)]) + data
                else:
                    body = bytes([fc | 0x80, 2])             # illegal address
            else:
                body = bytes([fc | 0x80, 1])                 # read-only simulator
            writer.write(struct.pack(">HHHB", tid, pid, len(body) + 1, unit) + body)
            await writer.drain()
    except (asyncio.IncompleteReadError, ConnectionResetError):
        pass
    finally:
        writer.close()


async def main():
    server = await asyncio.start_server(handle, HOST, PORT)
    total = sum(config.BLOCKS.values())
    print(f"Simulated TBox on {HOST}:{PORT}: ID 255 + blocks {list(config.BLOCKS)} "
          f"({total} DBoxes). Ctrl+C to stop.")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
