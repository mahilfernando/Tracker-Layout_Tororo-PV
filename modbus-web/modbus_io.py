"""Read the tags in config.TAGS from a Modbus TCP device."""

from pymodbus.client import ModbusTcpClient

import config


def to_signed(raw):
    """16-bit two's complement: 65535 -> -1."""
    return raw - 65536 if raw > 32767 else raw


def _read_block(client, kind, start, count):
    if kind == "input":
        rr = client.read_input_registers(start, count=count, device_id=config.UNIT_ID)
    else:
        rr = client.read_holding_registers(start, count=count, device_id=config.UNIT_ID)
    if rr.isError():
        raise IOError(f"device returned an error for {kind} {start}..{start + count - 1}: {rr}")
    return rr.registers


def read_tags(client):
    """Return {tag name: value in real units} for every tag in config.TAGS.

    Registers of the same kind are read in one request (from the lowest to the
    highest address), which is faster and kinder to the device than one request
    per tag. Keep each kind's addresses within 125 registers of each other.
    """
    values = {}
    for kind in ("holding", "input"):
        tags = [t for t in config.TAGS if t["kind"] == kind]
        if not tags:
            continue
        start = min(t["address"] for t in tags)
        count = max(t["address"] for t in tags) - start + 1
        regs = _read_block(client, kind, start, count)
        for t in tags:
            raw = regs[t["address"] - start]
            if t["signed"]:
                raw = to_signed(raw)
            values[t["name"]] = round(raw * t["scale"], 6)
    return values


def make_client():
    return ModbusTcpClient(config.DEVICE_IP, port=config.DEVICE_PORT, timeout=3)
