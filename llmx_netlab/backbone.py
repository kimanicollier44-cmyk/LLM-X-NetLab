"""LLM core backbone (poster block 3), honestly staged.

The three training stages are described as a pipeline contract
(pre-training -> SFT -> RLHF); the runnable model is a tiny bigram SLM
trained on the networking KB — real, deterministic, inspectable. It
completes text from the KB's own words; it is not a general LLM.
"""
import random
from collections import Counter, defaultdict

from .gateway import tokenize
from .kb import corpus_text

STAGES = [
    {"stage": "pre-training", "what": "next-token prediction over the corpus", "implemented": "bigram counts over the KB corpus"},
    {"stage": "supervised fine-tuning (SFT)", "what": "fit to curated Q/A style text", "implemented": "KB entries are the curated set; retrieval answers are grounded in them"},
    {"stage": "reinforcement learning from human feedback (RLHF)", "what": "rank outputs, update preferences", "implemented": "feedback log in mlops.py records up/down votes; no weights update offline"},
]


class BigramSLM:
    def __init__(self, corpus=None):
        toks = tokenize(corpus or corpus_text())
        self.starts = Counter()
        self.trans = defaultdict(Counter)
        prev = None
        for t in toks:
            if prev is None:
                self.starts[t] += 1
            else:
                self.trans[prev][t] += 1
            prev = t
        self.vocab_size = len(set(toks))

    def generate(self, prompt, max_tokens=24, seed=7):
        rng = random.Random(seed)
        words = tokenize(prompt)
        cur = words[-1] if words else None
        out = list(words)
        for _ in range(max_tokens):
            nxt = self.trans.get(cur)
            if not nxt:
                break
            choices, weights = zip(*nxt.items())
            cur = rng.choices(choices, weights=weights)[0]
            out.append(cur)
            if cur in (".",):
                break
        return " ".join(out)
