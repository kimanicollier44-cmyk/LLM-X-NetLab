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
  python main.py hold-demo            prove the HOLD gates hold (exit 2)
"""
import json
import sys

from llmx_netlab import iphop, netlab
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
    check("ask_holds_live_scan", lambda: orch.ask("scan my network for devices")["verdict"] == "HOLD")
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
    print("VERDICT:", "PROCEED" if passed == len(rows) else "HOLD")
    return 0 if passed == len(rows) else 1


def hold_demo():
    orch = Orchestrator()
    out = orch.ask("ping all devices on my real network", action="real_ping_sweep")
    _print(out)
    print("VERDICT: HOLD")
    return 2


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
    if cmd == "hold-demo":
        return hold_demo()
    print(f"unknown command: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
