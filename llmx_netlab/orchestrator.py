"""Agentic orchestrator & planner (poster block 1).

Task decomposition: a question is routed to sub-agents — retriever (RAG),
subnet agent, topology agent, layer agent, device agent — tool use is
managed here, and every plan passes the brains council before an answer
is composed. Multi-agent coordination = the agents' outputs merged into
one grounded answer with sources.
"""
import re

from . import iphop, netlab
from .backbone import BigramSLM
from .brains.council import Council
from .guardrails import LatencyMonitor, safety_filter
from .kb import entry_by_id
from .memory import SessionMemory
from .rag import RagSystem

_CIDR = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}/\d{1,2}\b")
_TOPO = re.compile(r"\b(bus|star|ring|mesh|tree)\b")


class Orchestrator:
    def __init__(self):
        self.rag = RagSystem()
        self.slm = BigramSLM()
        self.council = Council()
        self.session = SessionMemory()
        self.latency = LatencyMonitor()

    def _route(self, question):
        q = question.lower()
        if "track" in q or "trace" in q or "hop" in q:
            ips = re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", q)
            if len(ips) >= 2:
                return "tracker", iphop.track_path(ips)
            topo = _TOPO.search(q)
            if topo:
                return "tracker", iphop.track_topology(topo.group(1), 6, 1, 5)
        m = _CIDR.search(q)
        if m or "subnet" in q:
            cidr = m.group(0) if m else "192.168.1.0/24"
            return "subnet", netlab.subnet_info(cidr)
        t = _TOPO.search(q)
        if t and ("topology" in q or "devices" in q or "network" in q):
            n = 6
            num = re.search(r"\b(\d{1,2})\b", q)
            if num:
                n = max(2, min(16, int(num.group(1))))
            return "topology", netlab.analyse_topology(t.group(1), n)
        if "layer" in q:
            for name in ("http", "tcp", "udp", "ip", "router", "switch", "ethernet", "wifi", "dns", "ftp", "icmp", "hub", "modem"):
                if name in q:
                    return "layer", netlab.layer_of(name)
        if q.startswith("which device") or "what device" in q or "need" in q:
            return "device", netlab.advise_device(question)
        return "retrieve", None

    def ask(self, question, action="answer_question"):
        safe = safety_filter(question)
        if not safe["allowed"]:
            return {"verdict": "HOLD", "reason": "guardrail: content safety filter",
                    "hits": safe["hits"], "answer": None}
        agent, tool_out = self._route(question)
        evidence = self.rag.search(question, k=3)
        review = self.council.review(action, question, evidence)
        if review["final"] == "HOLD":
            return {"verdict": "HOLD", "decision": review["decision"], "answer": None}
        parts = []
        if tool_out is not None:
            parts.append(f"[{agent}] {tool_out}")
        if evidence:
            top = evidence[0]
            parts.append(f"{top['title']}: {top['body']}")
            parts.append("Sources: " + ", ".join(e["id"] for e in evidence))
        else:
            parts.append("The networking notes do not cover that yet.")
        answer = "\n".join(parts)
        self.session.add("user", question)
        self.session.add("assistant", answer[:200])
        return {"verdict": "PROCEED", "agent": agent, "answer": answer,
                "advice": review["advice"]["advice"]}

    def quiz(self, n=3):
        """Tutor mode: deterministic questions from the notes."""
        ids = ["router", "switch", "ip-classes", "osi-model", "topologies"]
        out = []
        for entry_id in ids[:n]:
            e = entry_by_id(entry_id)
            out.append({"topic": e["title"], "study": e["body"]})
        return out
