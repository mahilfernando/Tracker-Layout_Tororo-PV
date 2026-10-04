"""Read the PVH TBox over Modbus TCP. Read-only: nothing here writes registers."""

from pymodbus.client import ModbusTcpClient

import config
import tbox_map as m


def to_signed(raw):
    """16-bit two's complement: 65535 -> -1."""
    return raw - 65536 if raw > 32767 else raw


def make_client():
    return ModbusTcpClient(config.TBOX_IP, port=config.TBOX_PORT, timeout=config.TIMEOUT_S)


def read_range(client, unit_id, start, count):
    """Read `count` holding registers in chunks of config.REQUEST_SIZE."""
    regs = []
    for addr in range(start, start + count, config.REQUEST_SIZE):
        n = min(config.REQUEST_SIZE, start + count - addr)
        rr = client.read_holding_registers(addr, count=n, device_id=unit_id)
        if rr.isError():
            raise IOError(f"ID {unit_id}: error reading {addr}..{addr + n - 1}: {rr}")
        regs.extend(rr.registers)
    return regs


def _decode_tags(regs, start, tags):
    out = {}
    for name, offset, signed, scale, _unit in tags:
        raw = regs[offset - start]
        if signed:
            raw = to_signed(raw)
        out[name] = raw / scale if scale != 1 else raw
    return out


def read_global(client):
    regs = read_range(client, m.GLOBAL_UNIT_ID, m.GLOBAL_START, m.GLOBAL_COUNT)
    return _decode_tags(regs, m.GLOBAL_START, m.GLOBAL_TAGS)


def read_meteo0(client, block):
    regs = read_range(client, block, m.METEO0_START, m.METEO0_COUNT)
    return _decode_tags(regs, m.METEO0_START, m.METEO0_TAGS)


def read_block(client, block, dbox_count):
    """Return a list of dicts, one per DBox 1..dbox_count."""
    start = m.dbox_address(1)
    count = m.DBOX_STRIDE * (dbox_count - 1) + m.DBOX_USED
    regs = read_range(client, block, start, count)
    rows = []
    for n in range(1, dbox_count + 1):
        base = m.dbox_address(n) - start
        row = {"block": block, "dbox": n}
        for field, offset, signed, scale in m.DBOX_FIELDS:
            raw = regs[base + offset]
            if signed:
                raw = to_signed(raw)
            row[field] = raw / scale if scale != 1 else raw
        rows.append(row)
    return rows
