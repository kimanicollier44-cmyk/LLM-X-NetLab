"""Muse (Meta Model API) — the ADVISOR seat. Names-only, never overrides."""
import os


class MuseAdvisor:
    def __init__(self):
        self.key_present = bool(os.environ.get("MODEL_API_KEY"))

    def advise(self, question, evidence):
        titles = [e["title"] for e in evidence]
        advice = ("Ground the answer in the retrieved notes"
                  + (f" ({'; '.join(titles)})" if titles else " — and say when the notes do not cover it")
                  + ". Keep it at the notes' level: clear, short, example-first.")
        return {"brain": "muse", "role": "advisor", "advice": advice,
                "live_key_present": self.key_present, "authority": "none"}
