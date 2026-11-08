"""The NetLab engines: real networking math + OFFLINE simulation.

subnet calculator — network/broadcast/host counts, class, private check.
topology simulator — builds bus/star/ring/mesh/tree graphs, path + failure
analysis. layer mapper — protocol/device -> OSI + TCP/IP layer.
device advisor — need -> the notes' device. command simulator — ping and
tracert answered from a SIMULATED topology. Nothing here touches a real
network: no sockets are imported anywhere in this project.
"""
import ipaddress

from .kb import entry_by_id

PRIVATE_NETS = [ipaddress.ip_network(n) for n in
                ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]

CLASSES = [
    (1, 126, "A", "255.0.0.0", "large networks"),
    (128, 191, "B", "255.255.0.0", "medium networks"),
    (192, 223, "C", "255.255.255.0", "small networks"),
    (224, 239, "D", None, "multicast"),
    (240, 255, "E", None, "experimental"),
]


def ip_class(first_octet):
    for lo, hi, name, mask, use in CLASSES:
        if lo <= first_octet <= hi:
            return {"class": name, "default_mask": mask, "used_for": use}
    if first_octet == 127:
        return {"class": "loopback", "default_mask": None, "used_for": "loopback (127.0.0.1)"}
    return {"class": "reserved", "default_mask": None, "used_for": "reserved"}


def subnet_info(cidr):
    net = ipaddress.ip_network(cidr, strict=False)
    addr = ipaddress.ip_address(cidr.split("/")[0])
    hosts = max(net.num_addresses - 2, 0) if net.prefixlen < 31 else net.num_addresses
    return {
        "input": cidr,
        "network": str(net.network_address),
        "broadcast": str(net.broadcast_address),
        "netmask": str(net.netmask),
        "prefix": net.prefixlen,
        "addresses": net.num_addresses,
        "usable_hosts": hosts,
        "class": ip_class(int(str(addr).split(".")[0])) if addr.version == 4 else {"class": "IPv6"},
        "is_private": any(addr in p for p in PRIVATE_NETS) if addr.version == 4 else False,
        "is_loopback": addr.is_loopback,
        "version": addr.version,
    }


def build_topology(kind, n):
    """Return adjacency {node: set(neighbours)} for n devices (0 = first)."""
    if n < 2:
        raise ValueError("a topology needs at least 2 devices")
    adj = {i: set() for i in range(n)}

    def link(a, b):
        adj[a].add(b)
        adj[b].add(a)

    if kind == "bus":
        for i in range(n - 1):
            link(i, i + 1)          # the shared backbone, modelled as a chain
    elif kind == "star":
        for i in range(1, n):
            link(0, i)              # node 0 is the central device
    elif kind == "ring":
        for i in range(n):
            link(i, (i + 1) % n)
    elif kind == "mesh":
        for i in range(n):
            for j in range(i + 1, n):
                link(i, j)
    elif kind == "tree":
        for i in range(1, n):
            link((i - 1) // 2, i)   # binary-tree hierarchy
    else:
        raise ValueError(f"unknown topology: {kind}")
    return adj


def _path(adj, src, dst):
    from collections import deque
    seen = {src}
    q = deque([(src, [src])])
    while q:
        node, path = q.popleft()
        if node == dst:
            return path
        for nb in adj[node]:
            if nb not in seen:
                seen.add(nb)
                q.append((nb, path + [nb]))
    return None


def analyse_topology(kind, n):
    adj = build_topology(kind, n)
    links = sum(len(v) for v in adj.values()) // 2
    # single point of failure: a node whose removal disconnects the graph
    spof = []
    for cut in range(n):
        rest = {i: (adj[i] - {cut}) for i in range(n) if i != cut}
        nodes = list(rest)
        reached = set()
        stack = [nodes[0]] if nodes else []
        while stack:
            x = stack.pop()
            if x in reached:
                continue
            reached.add(x)
            stack.extend(rest[x] - reached)
        if len(reached) < len(nodes):
            spof.append(cut)
    worst = 0
    for i in range(n):
        for j in range(n):
            p = _path(adj, i, j)
            if p:
                worst = max(worst, len(p) - 1)
    return {"topology": kind, "devices": n, "links": links,
            "worst_case_hops": worst, "single_points_of_failure": spof}


LAYER_MAP = {
    # name -> (OSI layer, TCP/IP layer)
    "http": (7, 4), "https": (7, 4), "ftp": (7, 4), "dns": (7, 4),
    "tcp": (4, 3), "udp": (4, 3),
    "ip": (3, 2), "icmp": (3, 2),
    "router": (3, 2),
    "ethernet": (2, 1), "wifi": (2, 1), "switch": (2, 1),
    "hub": (1, 1), "repeater": (1, 1), "modem": (1, 1), "access point": (2, 1),
}


def layer_of(name):
    key = name.lower()
    if key not in LAYER_MAP:
        return None
    osi, tcpip = LAYER_MAP[key]
    return {"thing": key, "osi_layer": osi, "tcpip_layer": tcpip}


_NEEDS = [
    (("different networks", "between networks", "route"), "router"),
    (("same network", "connect devices", "wired devices"), "switch"),
    (("isp", "internet connection", "provider"), "modem"),
    (("wifi", "wireless"), "access point"),
    (("extend", "range", "far rooms"), "repeater"),
]


def advise_device(need):
    text = need.lower()
    for keys, device in _NEEDS:
        if any(k in text for k in keys):
            e = entry_by_id(device)
            return {"device": device, "from_notes": e["body"] if e else ""}
    return {"device": None, "from_notes": "No device in the notes matches that need."}


def simulate_ping(topology_kind, n, src, dst):
    """Ping answered from a simulated topology — never a real network."""
    adj = build_topology(topology_kind, n)
    path = _path(adj, src, dst)
    if path is None:
        return {"reachable": False, "path": None, "hops": None, "simulated": True}
    return {"reachable": True, "path": path, "hops": len(path) - 1, "simulated": True,
            "note": "answered from the simulated topology; no packet was sent"}
