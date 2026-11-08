"""IP address HOPPER, TRACKER and MAPPER.

hopper — walks a path hop by hop (a supplied IP list, or a path through
         a simulated topology) and analyses each hop.
tracker — the report Darion asked for by name: the START point, the
         MIDDLE point(s) and the ENDING point of the path, each mapped.
mapper — renders the tracked path as a text map + per-hop table.

Scope, stated plainly: paths come from data YOU supply or from this
lab's simulated topologies. Nothing probes, pings or geolocates a real
address — geolocate_real_ip / track_person_device / identify_ip_owner
are HOLD actions in the brains council.
"""
import ipaddress

from .netlab import PRIVATE_NETS, build_topology, ip_class, _path


def analyse_hop(ip, position, total):
    addr = ipaddress.ip_address(ip)
    if addr.version == 4:
        cls = ip_class(int(str(addr).split(".")[0]))["class"]
        private = any(addr in p for p in PRIVATE_NETS)
    else:
        cls, private = "IPv6", addr.is_private
    if position == 0:
        role = "START point — where the path begins (source side)"
    elif position == total - 1:
        role = "ENDING point — where the path ends (destination side)"
    else:
        role = "MIDDLE point — an intermediate hop (router/ gateway on the way)"
    return {"hop": position + 1, "ip": str(addr), "role": role,
            "class": cls, "is_private": private,
            "scope": "private/LAN" if private else "public/WAN"}


def track_path(ips):
    """Track a supplied path: start, middle(s), end — every hop mapped."""
    if len(ips) < 2:
        raise ValueError("a path needs at least a start and an ending point")
    hops = [analyse_hop(ip, i, len(ips)) for i, ip in enumerate(ips)]
    middle = hops[1:-1]
    return {
        "start": hops[0],
        "middle": middle,
        "middle_count": len(middle),
        "end": hops[-1],
        "total_hops": len(hops),
        "path": hops,
        "simulated": False,
        "source": "path supplied by the caller; analysed locally, never probed",
    }


def track_topology(kind, n, src, dst):
    """Track a path through a SIMULATED topology (start/middle/end)."""
    adj = build_topology(kind, n)
    path = _path(adj, src, dst)
    if path is None:
        return {"reachable": False, "simulated": True}
    ips = []
    for i, node in enumerate(path):
        if i == 0:
            ips.append("192.168.1.1")            # the source LAN gateway (modelled)
        elif i == len(path) - 1:
            ips.append("203.0.113.10")           # TEST-NET-3 documentation address (modelled destination)
        else:
            ips.append(f"10.0.{node}.1")         # private transit hops (modelled)
    out = track_path(ips)
    out["simulated"] = True
    out["topology"] = kind
    out["nodes"] = path
    out["source"] = "path through the simulated topology; addresses are modelled, not real"
    return out


def render_map(track):
    lines = ["IP PATH MAP (start -> middle -> end)"]
    for h in track["path"]:
        tag = "START" if h["hop"] == 1 else ("END" if h["hop"] == track["total_hops"] else f"hop {h['hop']}")
        lines.append(f"  [{tag:>5}] {h['ip']:<16} class {h['class']}  {h['scope']}")
    lines.append(f"  total hops: {track['total_hops']}  (middle points: {track['middle_count']})")
    return "\n".join(lines)
