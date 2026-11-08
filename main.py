#!/usr/bin/env python3
"""LLM-X-NetLab — ONE interface.

  python main.py demo                 end-to-end demo (ask + subnet + topology)
  python main.py ask "<question>"     orchestrated, council-reviewed answer
  python main.py subnet <cidr>        subnet calculator
  python main.py topology <kind> <n>  topology simulation + failure analysis
  python main.py layer <thing>        OSI / TCP-IP layer mapper
  python main.py device "<need>"      device advisor (from the notes)
  python main.py quiz                 tutor study cards
  python main.py track <ip,ip,...>    IP hopper/tracker/mapper: start, middle, end
  python main.py track-topo <kind> <n> <src> <dst>   track a simulated-topology path
  python main.py earth <ip,ip,...>    Google Earth KML export of the tracked path
  python main.py flow "<topic>"       Google Flow video plan for a notes topic
  python main.py bench                MLOps benchmark of the retriever
  python main.py stages               the backbone training-stage contract
  python main.py checks               self-checks (CHECKS n/n, RESULT, VERDICT)
  python main.py ping <host>          LIVE ping (icmp where permitted, else TCP timing)
  python main.py scan <host>          LIVE port scan of one named host
  python main.py trace <host>         LIVE traceroute -> tracker (start/middle/end)
  python main.py connect <host> <port>  LIVE TCP connect + latency
  python main.py dns <host>           LIVE DNS lookup
  python main.py http <url>           LIVE HTTP probe
  python main.py geo <ip>             LIVE IP geo lookup (approximate, ip-api.com)
"""
import json
import sys

from llmx_netlab import iphop, live, netlab
from llmx_netlab.earth import build_kml
from llmx_netlab.flowvideo import plan_video
from llmx_netlab.backbone import STAGES
from llmx_netlab.mlops import run_benchmark
from llmx_netlab.orchestrator import Orchestrator
from llmx_netlab.rag import RagSystem


def _print(obj):
    print(json.dumps(obj, indent=2) if isinstance(obj, (dict, list)) else obj)


def checks():
    rag = RagSystem()
    orch = Orchestrator()
    rows = []

    def check(name, fn):
        try:
            ok = bool(fn())
        except Exception:
            ok = False
        rows.append((name, ok))

    check("kb_loaded", lambda: len(rag.entries) >= 20)
    check("rag_finds_router", lambda: rag.search("What does a router do?")[0]["id"] == "router")
    check("subnet_math", lambda: netlab.subnet_info("192.168.1.0/24")["usable_hosts"] == 254)
    check("subnet_private", lambda: netlab.subnet_info("192.168.1.0/24")["is_private"] is True)
    check("subnet_public", lambda: netlab.subnet_info("8.8.8.0/24")["is_private"] is False)
    check("ip_class_c", lambda: netlab.subnet_info("192.168.1.0/24")["class"]["class"] == "C")
    check("star_spof_is_center", lambda: netlab.analyse_topology("star", 6)["single_points_of_failure"] == [0])
    check("mesh_no_spof", lambda: netlab.analyse_topology("mesh", 5)["single_points_of_failure"] == [])
    check("ring_hops", lambda: netlab.analyse_topology("ring", 6)["worst_case_hops"] == 3)
    check("layer_router", lambda: netlab.layer_of("router")["osi_layer"] == 3)
    check("ping_simulated", lambda: netlab.simulate_ping("star", 5, 1, 3)["simulated"] is True)
    check("ask_proceeds", lambda: orch.ask("What does a switch do?")["verdict"] == "PROCEED")
    check("ask_live_proceeds", lambda: orch.ask("ping localhost")["verdict"] == "PROCEED")
    import socket as _s
    _srv = _s.socket(); _srv.bind(("127.0.0.1", 0)); _srv.listen(1)
    _port = _srv.getsockname()[1]
    check("live_tcp_connect_loopback", lambda: live.tcp_connect("127.0.0.1", _port)["open"] is True)
    check("live_dns_localhost", lambda: "127.0.0.1" in live.dns_lookup("localhost")["addresses"])
    _srv.close()
    check("benchmark", lambda: run_benchmark(rag)["accuracy"] >= 0.8)
    _trk = iphop.track_path(["192.168.1.1", "10.0.0.1", "172.16.0.1", "203.0.113.10"])
    check("track_start", lambda: _trk["start"]["ip"] == "192.168.1.1" and "START" in _trk["start"]["role"])
    check("track_middle", lambda: _trk["middle_count"] == 2 and all("MIDDLE" in h["role"] for h in _trk["middle"]))
    check("track_end", lambda: _trk["end"]["ip"] == "203.0.113.10" and "ENDING" in _trk["end"]["role"])
    check("track_map_renders", lambda: "IP PATH MAP" in iphop.render_map(_trk))
    check("earth_kml", lambda: "<kml" in build_kml(_trk, {"192.168.1.1": (34.05, -118.24), "203.0.113.10": (40.71, -74.0)}))
    check("flow_plan", lambda: plan_video("star topology")["render"].startswith("HOLD"))
    check("carbon4_tiers", lambda: orch.council.decider.thinking_budget == 8192)
    passed = sum(1 for _, ok in rows if ok)
    for name, ok in rows:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"CHECKS {passed}/{len(rows)}")
    print("RESULT:", "PASS" if passed == len(rows) else "FAIL")
    print("VERDICT:", "PROCEED" if passed == len(rows) else "FAIL")
    return 0 if passed == len(rows) else 1


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    cmd = argv[1]
    orch = Orchestrator()
    if cmd == "demo":
        _print(orch.ask("What does a router do?"))
        _print(netlab.subnet_info("192.168.1.0/24"))
        _print(netlab.analyse_topology("star", 6))
        return 0
    if cmd == "ask":
        _print(orch.ask(" ".join(argv[2:])))
        return 0
    if cmd == "subnet":
        _print(netlab.subnet_info(argv[2]))
        return 0
    if cmd == "topology":
        _print(netlab.analyse_topology(argv[2], int(argv[3])))
        return 0
    if cmd == "layer":
        _print(netlab.layer_of(argv[2]))
        return 0
    if cmd == "device":
        _print(netlab.advise_device(" ".join(argv[2:])))
        return 0
    if cmd == "track":
        trk = iphop.track_path(argv[2].split(","))
        _print(trk)
        print(iphop.render_map(trk))
        return 0
    if cmd == "track-topo":
        trk = iphop.track_topology(argv[2], int(argv[3]), int(argv[4]), int(argv[5]))
        _print(trk)
        if trk.get("path"):
            print(iphop.render_map(trk))
        return 0
    if cmd == "earth":
        trk = iphop.track_path(argv[2].split(","))
        print(build_kml(trk))
        return 0
    if cmd == "flow":
        _print(plan_video(" ".join(argv[2:])))
        return 0
    if cmd == "quiz":
        _print(orch.quiz())
        return 0
    if cmd == "bench":
        _print(run_benchmark(orch.rag))
        return 0
    if cmd == "stages":
        _print(STAGES)
        return 0
    if cmd == "checks":
        return checks()
    if cmd == "ping":
        _print(live.ping_host(argv[2]))
        return 0
    if cmd == "scan":
        _print(live.port_scan(argv[2]))
        return 0
    if cmd == "trace":
        out = live.trace_and_track(argv[2])
        _print(out)
        if out.get("track"):
            print(iphop.render_map(out["track"]))
        return 0
    if cmd == "connect":
        _print(live.tcp_connect(argv[2], int(argv[3])))
        return 0
    if cmd == "dns":
        _print(live.dns_lookup(argv[2]))
        return 0
    if cmd == "http":
        _print(live.http_probe(argv[2]))
        return 0
    if cmd == "geo":
        _print(live.geo_lookup(argv[2]))
        return 0
    print(f"unknown command: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
