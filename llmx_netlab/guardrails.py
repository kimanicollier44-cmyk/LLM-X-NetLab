"""Guardrails & monitoring (poster block: support & safety layer).

content safety filter — refuses requests for live-network wrongdoing at
the text level too (defence in depth beside the HOLD gates).
PII redaction — emails / IPs-in-the-wild / long digit runs masked in logs.
latency monitoring — wraps a call, records elapsed ms.
"""
import re
import time

_BLOCKED = ("password of", "steal", "hack into", "break into", "spy on",
            "ddos", "flood the network")

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_DIGITS = re.compile(r"\b\d{7,}\b")


def safety_filter(text):
    low = text.lower()
    hits = [b for b in _BLOCKED if b in low]
    return {"allowed": not hits, "hits": hits}


def redact_pii(text):
    text = _EMAIL.sub("<email>", text)
    text = _DIGITS.sub("<number>", text)
    return text


class LatencyMonitor:
    def __init__(self):
        self.samples = []

    def measure(self, label, fn, *args, **kwargs):
        t0 = time.perf_counter()
        out = fn(*args, **kwargs)
        ms = (time.perf_counter() - t0) * 1000.0
        self.samples.append({"label": label, "ms": round(ms, 3)})
        return out

    def summary(self):
        if not self.samples:
            return {"calls": 0, "avg_ms": 0.0, "max_ms": 0.0}
        vals = [s["ms"] for s in self.samples]
        return {"calls": len(vals), "avg_ms": round(sum(vals) / len(vals), 3),
                "max_ms": max(vals)}
