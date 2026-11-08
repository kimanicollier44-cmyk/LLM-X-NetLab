"""Live networking — real sockets, online at Darion's direction (v1.1.0).

Functions: DNS lookup, TCP connect + latency, port scan of a named host,
ping (system binary where permitted, TCP-timing fallback, both labelled),
traceroute (TTL-stepped probes; hops feed the IP tracker as START /
MIDDLE / END), HTTP probe, and IP geo lookup (public geo API, approximate,
infrastructure-level: country/city/ISP — the same data any IP-lookup
site shows).

Engineering limits (not gates): one host per scan, sweeps capped at a
/24, short timeouts, modest thread count.
"""
import json
import socket
import subprocess
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995,
                1723, 3306, 3389, 5900, 8000, 8080, 8443]


def dns_lookup(host):
    infos = socket.getaddrinfo(host, None)
    ips = sorted({i[4][0] for i in infos})
    out = {"host": host, "addresses": ips}
    try:
        out["canonical"] = socket.gethostbyname_ex(host)[0]
    except OSError:
        pass
    try:
        out["reverse"] = socket.gethostbyaddr(ips[0])[0] if ips else None
    except OSError:
        out["reverse"] = None
    return out


def tcp_connect(host, port, timeout=3.0):
    t0 = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            ms = (time.perf_counter() - t0) * 1000
            return {"host": host, "port": port, "open": True, "ms": round(ms, 2)}
    except OSError as e:
        ms = (time.perf_counter() - t0) * 1000
        return {"host": host, "port": port, "open": False, "ms": round(ms, 2),
                "error": type(e).__name__}


def port_scan(host, ports=None, timeout=1.5, workers=32):
    ports = ports or COMMON_PORTS
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda p: tcp_connect(host, p, timeout), ports))
    open_ports = [r for r in results if r["open"]]
    return {"host": host, "scanned": len(ports), "open": open_ports,
            "open_count": len(open_ports)}


def ping_host(host, count=4, fallback_ports=(443, 80)):
    """ICMP ping via the system binary where the machine permits it;
    otherwise a TCP connect-timing fallback. The method is labelled."""
    try:
        proc = subprocess.run(["ping", "-c", str(count), "-W", "2", host],
                              capture_output=True, text=True, timeout=30)
        if proc.returncode == 0 and "time=" in proc.stdout:
            times = []
            for line in proc.stdout.splitlines():
                if "time=" in line:
                    times.append(float(line.split("time=")[1].split()[0]))
            return {"host": host, "method": "icmp (system ping)",
                    "replies": len(times), "sent": count,
                    "min_ms": min(times), "avg_ms": round(sum(times) / len(times), 3),
                    "max_ms": max(times)}
        icmp_error = (proc.stderr or proc.stdout).strip().splitlines()[-1][:120]
    except Exception as e:  # noqa: BLE001 - fall through to the TCP method
        icmp_error = f"{type(e).__name__}: {e}"
    samples = []
    for port in fallback_ports:
        r = tcp_connect(host, port, timeout=3.0)
        if r["open"]:
            samples.append(r["ms"])
            break
    return {"host": host, "method": "tcp timing (icmp unavailable here)",
            "icmp_note": icmp_error, "reachable": bool(samples),
            "ms": samples[0] if samples else None}


def _ping_ttl_reply(host, ttl, timeout=2):
    """One TTL-stepped ping; returns the responder IP or None.
    Uses the system ping (-t sets TTL); needs a working ping binary."""
    try:
        proc = subprocess.run(["ping", "-c", "1", "-t", str(ttl), "-W", str(timeout), host],
                              capture_output=True, text=True, timeout=timeout + 5)
    except Exception:  # noqa: BLE001
        return None, False
    out = proc.stdout
    reached = "time=" in out and proc.returncode == 0
    responder = None
    for line in out.splitlines():
        if "From " in line and ("Time to live exceeded" in line or "exceeded" in line):
            responder = line.split("From ")[1].split()[0].strip(":")
        if line.startswith("PING") and reached:
            responder = host
    return responder, reached


def traceroute(host, max_hops=20):
    """TTL-stepped traceroute. Methods, in order: system ping per-TTL;
    if the environment forbids ICMP entirely, the trace reports the
    start (this machine's target resolution) and the END (TCP-confirmed)
    and says the middle could not be heard here."""
    target_ip = socket.gethostbyname(host)
    hops = []
    method = "icmp-ttl (system ping)"
    reached = False
    for ttl in range(1, max_hops + 1):
        responder, hit = _ping_ttl_reply(host, ttl)
        if responder is None and ttl == 1:
            method = "unavailable-in-this-environment"
            break
        hops.append({"hop": ttl, "ip": responder})
        if hit or responder == target_ip:
            reached = True
            break
    if method == "unavailable-in-this-environment":
        conn = tcp_connect(host, 443, timeout=3.0)
        return {"host": host, "target_ip": target_ip, "method": method,
                "note": "ICMP is blocked in this environment (no CAP_NET_RAW); "
                        "on a normal Linux/Termux, ping-based tracing works. "
                        "END confirmed by TCP connect.",
                "hops": [], "reached_end": conn["open"], "end_check": conn}
    return {"host": host, "target_ip": target_ip, "method": method,
            "hops": hops, "reached_end": reached}


def http_probe(url, timeout=6.0):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    req = urllib.request.Request(url, headers={"User-Agent": "LLM-X-NetLab/1.1"})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(2048)
            return {"url": url, "status": r.status, "ms": round((time.perf_counter() - t0) * 1000, 2),
                    "server": r.headers.get("Server"), "content_type": r.headers.get("Content-Type"),
                    "bytes_read": len(body), "final_url": r.geturl()}
    except Exception as e:  # noqa: BLE001
        return {"url": url, "status": None, "error": f"{type(e).__name__}: {e}",
                "ms": round((time.perf_counter() - t0) * 1000, 2)}


def geo_lookup(ip):
    """Approximate location of an IP via a public geo API — country,
    region, city, ISP/org. Router/hop-level data, always labelled
    approximate; not a person's address."""
    url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,org,as,query,lat,lon"
    try:
        with urllib.request.urlopen(url, timeout=6) as r:
            d = json.load(r)
        if d.get("status") != "success":
            return {"ip": ip, "found": False}
        return {"ip": ip, "found": True, "country": d.get("country"),
                "region": d.get("regionName"), "city": d.get("city"),
                "isp": d.get("isp"), "org": d.get("org"), "as": d.get("as"),
                "lat": d.get("lat"), "lon": d.get("lon"),
                "accuracy": "approximate — city-level, as published by ip-api.com"}
    except Exception as e:  # noqa: BLE001
        return {"ip": ip, "found": False, "error": f"{type(e).__name__}: {e}"}


def trace_and_track(host, max_hops=20):
    """Traceroute, then feed the discovered hop IPs into the tracker so
    the path reads START / MIDDLE / END with classes and scopes."""
    from .iphop import track_path
    tr = traceroute(host, max_hops=max_hops)
    out = {"traceroute": tr}
    ips = [h["ip"] for h in tr.get("hops", []) if h.get("ip")]
    if ips and ips[-1] != tr["target_ip"]:
        ips.append(tr["target_ip"])
    if len(ips) >= 2:
        out["track"] = track_path(ips)
    return out
