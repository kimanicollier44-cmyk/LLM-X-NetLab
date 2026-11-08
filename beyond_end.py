#!/usr/bin/env python3
"""LLM-X-NetLab — BEYOND THE END POINT.

PRIVATE — contains Darion's real home-network addresses. Do not publish.

Darion's rule: "After end point — public IPs connect to all other end
points until it can't connect."

How that actually works on the internet (honest mechanics): you cannot
remote-control an ISP router and order it to connect onward. The way a
path keeps going, endpoint to endpoint, is TTL stepping — traceroute.
Each hop either (a) reveals the next endpoint, (b) is the destination
answering, or (c) goes silent. The walk stops at the first place it
can't connect, and this script records exactly where and why:

    REACHED            the endpoint itself answered — path complete
    SILENT             3 hops in a row answered nothing (ICMP filtered
                       or off) — can't connect further *that way*
    MAX HOPS           still going at hop 30 — cut off by the limit
    ENV BLOCKED        this machine forbids ICMP here (e.g. a sandbox
                       with no CAP_NET_RAW) — run it on the LAN/Termux

After the traces, every unique endpoint discovered gets a direct TCP
connect test (port 443): CONNECTS vs NO SERVICE (a routing-only
endpoint — most core routers answer hops but run no public service;
that is normal, not a failure).

Run from inside your llm-x-netlab folder, ON the home LAN:

    python3 beyond_end.py              # full walk + report file
    python3 beyond_end.py --selftest   # logic check, no network

Writes beyond-end-report-YYYYmmdd-HHMMSS.txt next to this file.
"""
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent

ORIGIN_PUBLIC_IP = "172.117.13.152"  # Darion's public IP (dynamic)
TARGETS = [
    ("1.1.1.1",        "Cloudflare DNS (anycast)"),
    ("8.8.8.8",        "Google DNS (anycast)"),
    ("9.9.9.9",        "Quad9 DNS (anycast)"),
    ("208.67.222.222", "OpenDNS (anycast)"),
    ("198.41.0.4",     "A-root DNS server"),
    ("github.com",     "GitHub (host, resolves to an endpoint)"),
]
MAX_HOPS = 30
SILENT_LIMIT = 3
GEO_LIMIT = 15


def stop_reason(trace):
    """Classify how one trace ended, in Darion's terms."""
    if trace.get("method") == "unavailable-in-this-environment":
        return "ENV BLOCKED"
    hops = trace.get("hops", [])
    if trace.get("reached_end"):
        return "REACHED"
    silent = 0
    for h in reversed(hops):
        if h.get("ip") is None:
            silent += 1
        else:
            break
    if silent >= SILENT_LIMIT:
        return "SILENT"
    if len(hops) >= MAX_HOPS:
        return "MAX HOPS"
    return "SILENT" if hops else "ENV BLOCKED"


def merge_endpoints(traces):
    """All unique endpoints across traces, with first-seen hop distance."""
    seen = {}
    for name, trace in traces:
        for h in trace.get("hops", []):
            ip = h.get("ip")
            if ip and ip not in seen:
                seen[ip] = {"ip": ip, "first_hop": h["hop"], "via": name,
                            "paths": 1}
            elif ip:
                seen[ip]["paths"] += 1
    return sorted(seen.values(), key=lambda e: (e["first_hop"], e["ip"]))


FAKE = [
    ("dest-a", {"method": "icmp-ttl (system ping)", "reached_end": True,
                "hops": [{"hop": 1, "ip": "192.168.1.1"},
                         {"hop": 2, "ip": "10.0.0.1"},
                         {"hop": 3, "ip": "172.117.13.1"},
                         {"hop": 4, "ip": "1.1.1.1"}]}),
    ("dest-b", {"method": "icmp-ttl (system ping)", "reached_end": False,
                "hops": [{"hop": 1, "ip": "192.168.1.1"},
                         {"hop": 2, "ip": "10.0.0.1"},
                         {"hop": 3, "ip": None},
                         {"hop": 4, "ip": None},
                         {"hop": 5, "ip": None}]}),
]


def selftest():
    eps = merge_endpoints(FAKE)
    assert stop_reason(FAKE[0][1]) == "REACHED", stop_reason(FAKE[0][1])
    assert stop_reason(FAKE[1][1]) == "SILENT", stop_reason(FAKE[1][1])
    assert eps[0]["ip"] == "192.168.1.1" and eps[0]["paths"] == 2
    assert any(e["ip"] == "1.1.1.1" for e in eps)
    print("SELFTEST PASS — stop rules + endpoint merge behave:")
    for e in eps:
        print(f"  hop {e['first_hop']:>2}  {e['ip']:<16} in {e['paths']} path(s), first via {e['via']}")
    print(f"  dest-a -> {stop_reason(FAKE[0][1])} · dest-b -> {stop_reason(FAKE[1][1])}")
    return 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    sys.path.insert(0, str(HERE))
    try:
        from llmx_netlab import live
    except ImportError:
        print("Run me from inside the llm-x-netlab folder.")
        return 2

    lines = [
        "BEYOND THE END POINT — endpoint walk",
        f"Origin (after END): Darion's public IP {ORIGIN_PUBLIC_IP}",
        f"When: {datetime.now().isoformat(timespec='seconds')}",
        "Rule: keep connecting endpoint to endpoint until it can't.",
        "=" * 70,
    ]
    traces = []
    for host, label in TARGETS:
        print(f"--- tracing {host} ({label}) ...", flush=True)
        tr = live.traceroute(host, max_hops=MAX_HOPS)
        traces.append((host, tr))
        reason = stop_reason(tr)
        lines.append(f"\n### {host} — {label}  ->  {reason}")
        for h in tr.get("hops", []):
            lines.append(f"  hop {h['hop']:>2}  {h.get('ip') or '* * * (silent)'}")
        if tr.get("method") == "unavailable-in-this-environment":
            lines.append("  " + tr.get("note", ""))

    endpoints = merge_endpoints(traces)
    lines.append(f"\n{'=' * 70}\nENDPOINT MAP — {len(endpoints)} unique endpoints discovered")
    for e in endpoints:
        conn = live.tcp_connect(e["ip"], 443, timeout=2.0)
        e["connect443"] = "CONNECTS" if conn["open"] else "NO SERVICE"
        lines.append(f"  hop {e['first_hop']:>2}  {e['ip']:<16} {e['connect443']:<10} "
                     f"in {e['paths']} path(s), first via {e['via']}")

    lines.append(f"\nGEO — first {GEO_LIMIT} endpoints (approximate, city-level)")
    for e in endpoints[:GEO_LIMIT]:
        g = live.geo_lookup(e["ip"])
        if g.get("found"):
            lines.append(f"  {e['ip']:<16} {g.get('city')}, {g.get('region')} — "
                         f"{g.get('isp')} ({g.get('as')})")
        else:
            lines.append(f"  {e['ip']:<16} no geo published")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report = HERE / f"beyond-end-report-{stamp}.txt"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nDONE — report saved to {report.name}")
    print(f"Endpoints discovered: {len(endpoints)} · "
          f"connect on 443: {sum(1 for e in endpoints if e['connect443'] == 'CONNECTS')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
