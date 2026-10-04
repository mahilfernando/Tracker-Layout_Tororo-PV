"""Find Modbus TCP devices on the local network and spot the PVH TBox.

    python find_tbox.py                     # scans 192.168.1.1-254
    python find_tbox.py --subnet 10.0.0     # scans 10.0.0.1-254
    python find_tbox.py --hosts 192.168.1.60 192.168.1.21

For every host with port 502 (or 503) open, it reads a few holding
registers. A TBox answers on Modbus ID 255 with its UTC date and time at
40000-40005 (year, month, day, hour, minute, second).

Read-only: it only reads registers.
"""

import argparse
import socket
from concurrent.futures import ThreadPoolExecutor

from pymodbus.client import ModbusTcpClient


def port_open(host, port, timeout):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def try_read(host, port, unit, address, count=6):
    client = ModbusTcpClient(host, port=port, timeout=2)
    try:
        if not client.connect():
            return None
        rr = client.read_holding_registers(address, count=count, device_id=unit)
        return None if rr.isError() else rr.registers
    except Exception:
        return None
    finally:
        client.close()


def looks_like_date(r):
    return r and 2020 <= r[0] <= 2100 and 1 <= r[1] <= 12 and 1 <= r[2] <= 31 and r[3] <= 23 and r[4] <= 59


def fmt_date(r):
    return f"{r[0]:04d}-{r[1]:02d}-{r[2]:02d} {r[3]:02d}:{r[4]:02d}:{r[5]:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subnet", default="192.168.1", help="first three parts of the IP, e.g. 192.168.1")
    ap.add_argument("--hosts", nargs="*", help="check only these IPs")
    ap.add_argument("--ports", nargs="*", type=int, default=[502, 503])
    ap.add_argument("--timeout", type=float, default=0.5)
    args = ap.parse_args()

    hosts = args.hosts or [f"{args.subnet}.{i}" for i in range(1, 255)]
    targets = [(h, p) for h in hosts for p in args.ports]
    print(f"Checking {len(hosts)} hosts on ports {args.ports} …")
    with ThreadPoolExecutor(max_workers=64) as pool:
        found = [t for t, ok in zip(targets, pool.map(lambda t: port_open(*t, args.timeout), targets)) if ok]

    if not found:
        print("No Modbus TCP devices found. Check that this PC is on the same network.")
        return

    print(f"\n{len(found)} Modbus port(s) open:\n")
    candidates = []
    for host, port in found:
        print(f"{host}:{port}")
        tbox = try_read(host, port, 255, 0)
        if looks_like_date(tbox):
            print(f"   ID 255 @40000: {fmt_date(tbox)}  <-- looks like a PVH TBox (plant status)")
            candidates.append(f"{host}:{port}")
        elif tbox:
            print(f"   ID 255 @40000: {tbox}")
        else:
            print("   ID 255: no answer")
        for unit, addr, label in ((1, 0, "ID 1 @40000"), (1, 5000, "ID 1 @45000")):
            regs = try_read(host, port, unit, addr)
            if regs:
                extra = f"  ({fmt_date(regs)})" if looks_like_date(regs) else ""
                print(f"   {label}: {regs}{extra}")

    print()
    if candidates:
        print("TBox candidate(s):", ", ".join(candidates))
        print("Put the IP in config.py (TBOX_IP) and run read_test.py.")
    else:
        print("No device answered like a TBox on ID 255. Send the output above for help.")


if __name__ == "__main__":
    main()
