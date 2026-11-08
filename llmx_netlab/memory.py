"""Memory systems (poster block 5).

Session memory = short-term, in-RAM conversation turns.
Episodic memory = long-term JSON file store, used only when the caller
passes an explicit path (nothing is written by default).
"""
import json
import os
import time


class SessionMemory:
    def __init__(self, max_turns=20):
        self.turns = []
        self.max_turns = max_turns

    def add(self, role, text):
        self.turns.append({"role": role, "text": text})
        self.turns = self.turns[-self.max_turns:]

    def context(self):
        return "\n".join(f"{t['role']}: {t['text']}" for t in self.turns)


class EpisodicMemory:
    def __init__(self, path):
        self.path = path
        self.events = []
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.events = json.load(f)

    def record(self, kind, detail):
        self.events.append({"ts": time.time(), "kind": kind, "detail": detail})
        if self.path:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.events, f)

    def recall(self, kind=None):
        return [e for e in self.events if kind is None or e["kind"] == kind]
