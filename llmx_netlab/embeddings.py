"""Embedding model seat: from-scratch TF-IDF vectors + cosine similarity.

Stands in for the poster's EMBEDDING MODELS box with real, inspectable
math — no external model, no downloads.
"""
import math
from collections import Counter

from .gateway import tokenize


class TfidfEmbedder:
    def __init__(self, documents):
        self.docs = [tokenize(d) for d in documents]
        self.n = len(self.docs)
        df = Counter()
        for toks in self.docs:
            for t in set(toks):
                df[t] += 1
        self.idf = {t: math.log((self.n + 1) / (c + 1)) + 1.0 for t, c in df.items()}

    def embed(self, text):
        toks = tokenize(text)
        if not toks:
            return {}
        tf = Counter(toks)
        return {t: (c / len(toks)) * self.idf.get(t, 1.0) for t, c in tf.items()}


def cosine(a, b):
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(t, 0.0) for t, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
