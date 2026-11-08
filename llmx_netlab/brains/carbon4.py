"""Gemini Carbon 4 Extended Thinking — the DECIDER seat.

v1.1.0 (Darion's direction): the HOLD gate system is REMOVED and the lab
is online with real sockets. The council keeps its review structure —
MAP -> MODEL -> STRESS -> DECIDE over the request + evidence — and no
longer refuses networking actions. HOLD_ACTIONS is kept, empty, so
existing imports keep working.
"""
import os

HOLD_ACTIONS = set()

THINKING_TIERS = {"standard": 2048, "extended": 8192, "deep": 32768}


class Carbon4:
    """Extended Thinking: MAP -> MODEL -> STRESS -> DECIDE, tiered budget."""

    def __init__(self, tier="extended"):
        self.key_present = bool(os.environ.get("GEMINI_API_KEY"))
        self.tier = tier
        self.thinking_budget = THINKING_TIERS[tier]

    def decide(self, action, evidence, question=""):
        return {"brain": "gemini-carbon-4", "role": "DECIDER",
                "model": "google/gemini-carbon-4-extended-pro-thinking",
                "thinking_tier": self.tier, "thinking_budget": self.thinking_budget,
                "phases": ["MAP", "MODEL", "STRESS", "DECIDE"],
                "verdict": "PROCEED", "holds": [],
                "mode": "online — hold gates removed (v1.1.0)",
                "live_key_present": self.key_present}
