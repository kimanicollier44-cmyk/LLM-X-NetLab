"""MLOps & continuous learning (poster block: support layer).

evaluation & benchmarking — a fixed question set graded against the RAG
system (top-1 hit must be the expected KB entry).
model deployment — descriptor only; this lab ships as source + container.
online learning — a feedback log (JSONL in memory) that records votes;
entries can be promoted into the KB by a human, never automatically.
"""
import json

BENCHMARK = [
    ("What does a router do?", "router"),
    ("Which device connects devices in the same network?", "switch"),
    ("What are the private IP ranges?", "ip-addressing"),
    ("Explain the OSI model layers", "osi-model"),
    ("Bus star ring mesh are what?", "topologies"),
    ("What is bandwidth measured in?", "bandwidth"),
    ("Name the firewall types", "firewall-types"),
    ("What does ping check?", "commands"),
    ("TCP/IP model has how many layers?", "tcpip-model"),
    ("Class C subnet mask?", "ip-classes"),
]


def run_benchmark(rag):
    rows = []
    for question, expected in BENCHMARK:
        hits = rag.search(question, k=1)
        got = hits[0]["id"] if hits else None
        rows.append({"question": question, "expected": expected, "got": got,
                     "pass": got == expected})
    passed = sum(r["pass"] for r in rows)
    return {"passed": passed, "total": len(rows),
            "accuracy": round(passed / len(rows), 3), "rows": rows}


class FeedbackLog:
    def __init__(self):
        self.lines = []

    def vote(self, question, helpful):
        self.lines.append(json.dumps({"question": question, "helpful": bool(helpful)}))

    def tally(self):
        up = sum(1 for ln in self.lines if json.loads(ln)["helpful"])
        return {"votes": len(self.lines), "helpful": up}
