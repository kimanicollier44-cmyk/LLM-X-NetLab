#!/usr/bin/env python3
"""LLM-X-NetLab — ALL RECOMMENDED SCRIPTS, updated for Darion's home LAN.

PRIVATE — contains Darion's real home-network addresses. Do not publish.

Run it from inside your llm-x-netlab folder (Termux or any machine that is
ON the home LAN — direct sockets give real answers there):

    git clone https://github.com/credkellar/LLM-X-NetLab.git   (once)
    cd LLM-X-NetLab
    cp /path/to/run_recommended.py .
    python3 run_recommended.py

It runs every recommended command from the LAN map + ISP architecture
docs, with the real addresses baked in, and writes a timestamped report
next to this file: netlab-report-YYYYmmdd-HHMMSS.txt

Sections:
  1. Self-checks            python main.py checks
  2. Subnet                 python main.py subnet 192.168.1.0/24
  3. Path tracker           phone -> gateway -> public (START/MIDDLE/END)
  4. Router scan + ping     the first live test: 192.168.1.1
  5. Per-device port scan   all 10 KEEP addresses
  6. ISP path trace         python main.py trace 1.1.1.1
                            (hops 2-5 expose the modem/CMTS/metro layer
                            that the ISP architecture doc marks INFERRED)
  7. Geo of the public IP   python main.py geo 172.117.13.152
                            (note: the public IP is dynamic — if it has
                            changed, update PUBLIC_IP below and in the
                            LAN map)
"""
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --- Darion's network (KEEP list, 2026-11-08) ------------------------------
ROUTER = "192.168.1.1"
SUBNET = "192.168.1.0/24"
PUBLIC_IP = "172.117.13.152"  # dynamic — refresh from Fing if it changes
DEVICES = [
    ("192.168.1.1",   "router — Askey SAX1V1K (gateway/DNS/DHCP)"),
    ("192.168.1.61",  "Galaxy A16 5G"),
    ("192.168.1.106", "vl68-pro"),
    ("192.168.1.120", "vl68-pro-11"),
    ("192.168.1.156", "iPhone 11 — Darion"),
    ("192.168.1.182", "Xumo Stream Box"),
    ("192.168.1.195", "stratus-c8-prime"),
    ("192.168.1.215", "Galaxy S22"),
    ("192.168.1.232", "Moto G 2026"),
    ("192.168.1.234", "Echo Show"),
]
PATH = "192.168.1.156,192.168.1.1," + PUBLIC_IP  # START,MIDDLE,END

COMMANDS = [
    ("1. Self-checks",            ["checks"]),
    ("2. Subnet — home LAN",      ["subnet", SUBNET]),
    ("3. Tracker — my path out",  ["track", PATH]),
    ("4a. Router — port scan",    ["scan", ROUTER]),
    ("4b. Router — ping",         ["ping", ROUTER]),
] + [
    (f"5. Scan — {name} ({ip})",  ["scan", ip]) for ip, name in DEVICES[1:]
] + [
    ("6. Trace — ISP path to 1.1.1.1 (CMTS/metro ground truth)", ["trace", "1.1.1.1"]),
    ("7. Geo — public IP",        ["geo", PUBLIC_IP]),
]


def main() -> int:
    if not (HERE / "main.py").exists():
        print("Run me from inside the llm-x-netlab folder (main.py not found here).")
        return 2
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report = HERE / f"netlab-report-{stamp}.txt"
    lines = [
        "LLM-X-NetLab — recommended run for SpectrumSetup-03",
        f"When: {datetime.now().isoformat(timespec='seconds')}",
        f"Where: run on the home LAN (direct sockets) — results are real.",
        "=" * 70,
    ]
    for title, args in COMMANDS:
        cmd = [sys.executable, "main.py", *args]
        lines.append(f"\n### {title}\n$ python main.py {' '.join(args)}")
        print(f"--- {title} ...", flush=True)
        t0 = time.time()
        r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, timeout=300)
        out = (r.stdout or "") + (r.stderr or "")
        lines.append(out.rstrip())
        lines.append(f"[exit {r.returncode} · {time.time() - t0:.1f}s]")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nDONE — full report saved to {report.name}")
    print("Send that report file back to Muse and the ISP architecture")
    print("doc's INFERRED hops get replaced with your real traceroute.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
