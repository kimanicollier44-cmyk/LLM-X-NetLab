"""Retrieval-Augmented Generation system (poster block 4).

Vector database = the TF-IDF store over KB chunks (semantic search).
Knowledge graph = explicit topic relations between KB entries.
External knowledge bases = registered by name only; nothing is fetched.
"""
from .embeddings import TfidfEmbedder, cosine
from .kb import all_entries

# topic relations distilled from the notes' own cross-references
GRAPH_EDGES = [
    ("router", "routing-vs-switching"), ("switch", "routing-vs-switching"),
    ("router", "devices-overview"), ("switch", "devices-overview"),
    ("ip-addressing", "ip-classes"), ("ip-classes", "protocols"),
    ("osi-model", "tcpip-model"), ("tcpip-model", "protocols"),
    ("firewall-types", "network-security"), ("network-security", "network-kinds"),
    ("topologies", "devices-overview"), ("commands", "ip-addressing"),
    ("bandwidth", "network-kinds"), ("internet-services", "protocols"),
]


class RagSystem:
    def __init__(self, entries=None):
        self.entries = entries or all_entries()
        texts = [f"{e['title']} {e['body']} {' '.join(e['tags'])}" for e in self.entries]
        self.embedder = TfidfEmbedder(texts)
        self.vectors = [self.embedder.embed(t) for t in texts]
        self.graph = {}
        for a, b in GRAPH_EDGES:
            self.graph.setdefault(a, set()).add(b)
            self.graph.setdefault(b, set()).add(a)

    def search(self, query, k=3):
        q = self.embedder.embed(query)
        scored = [(cosine(q, v), e) for v, e in zip(self.vectors, self.entries)]
        scored.sort(key=lambda s: s[0], reverse=True)
        return [{"score": round(s, 4), "id": e["id"], "title": e["title"], "body": e["body"]}
                for s, e in scored[:k] if s > 0]

    def related(self, entry_id):
        return sorted(self.graph.get(entry_id, set()))
