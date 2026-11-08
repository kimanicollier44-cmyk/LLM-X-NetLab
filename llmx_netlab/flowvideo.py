"""Google Flow seat — explainer-video PLANNING for networking topics.

Builds a storyboard + Veo-style prompts + a 4-track timeline for a
topic from the notes (e.g. 'how a packet crosses a star topology').
Plan only: live generation is a HOLD action in spirit — rendering
needs Darion's own Google Flow access and is never attempted here.
"""
from .rag import RagSystem

TRACKS = ["setup", "explain", "diagram", "recap"]


def plan_video(topic, rag=None):
    rag = rag or RagSystem()
    hits = rag.search(topic, k=2)
    source = hits[0] if hits else None
    scenes = [
        {"track": "setup", "seconds": 6,
         "prompt": f"Title card: '{topic}' over a clean desk with a router, switch and laptop, soft classroom light"},
        {"track": "explain", "seconds": 20,
         "prompt": f"Narrated walkthrough of {topic}, simple diagrams appearing step by step"
                   + (f", grounded in the notes entry '{source['title']}'" if source else "")},
        {"track": "diagram", "seconds": 14,
         "prompt": f"Animated diagram for {topic}: devices light up in order as data flows between them"},
        {"track": "recap", "seconds": 8,
         "prompt": "Recap card with the three key points, then 'Stay connected, stay learning, keep coding'"},
    ]
    return {"topic": topic, "tracks": TRACKS, "scenes": scenes,
            "total_seconds": sum(s["seconds"] for s in scenes),
            "grounded_in": source["id"] if source else None,
            "render": "HOLD — plan only; live generation needs your own Google Flow access"}
