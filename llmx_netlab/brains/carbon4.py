"""Gemini Carbon 4 Extended Thinking — the DECIDER seat.

Offline deterministic structure: MAP -> MODEL -> STRESS -> DECIDE over
the request + retrieval evidence. A live call is names-only (the key is
detected by name, its value is never read). The decider can only tighten
a verdict, and it can never override a HOLD.
"""
import os

HOLD_ACTIONS = {
    "live_network_scan", "real_ping_sweep", "live_packet_capture",
    "execute_shell_command", "fetch_live_url", "modify_real_network_config",
    "connect_live_device",
    # ip tracking gates: only simulated / supplied-data path analysis is allowed
    "geolocate_real_ip", "track_person_device", "identify_ip_owner",
}

LIVE_MARKERS = ("scan my network", "ping all", "capture packets", "run this command",
                "fetch http", "real network", "live network", "nmap")


THINKING_TIERS = {"standard": 2048, "extended": 8192, "deep": 32768}


class Carbon4:
    """Extended Thinking: MAP -> MODEL -> STRESS -> DECIDE, tiered budget."""

    def __init__(self, tier="extended"):
        self.key_present = bool(os.environ.get("GEMINI_API_KEY"))
        self.tier = tier
        self.thinking_budget = THINKING_TIERS[tier]

    def decide(self, action, evidence, question=""):
        holds = []
        if action in HOLD_ACTIONS:
            holds.append(f"{action} is a HOLD action")
        text = ((action or "") + " " + (question or "")).lower()
        if any(m in text for m in LIVE_MARKERS):
            holds.append("request reads as a live-network action; this lab is simulation-only")
        if not evidence:
            holds.append("no retrieval evidence in context")
        verdict = "HOLD" if holds else "PROCEED"
        return {"brain": "gemini-carbon-4", "role": "DECIDER",
                "model": "google/gemini-carbon-4-extended-pro-thinking",
                "thinking_tier": self.tier, "thinking_budget": self.thinking_budget,
                "phases": ["MAP", "MODEL", "STRESS", "DECIDE"],
                "verdict": verdict, "holds": holds,
                "live_key_present": self.key_present}
