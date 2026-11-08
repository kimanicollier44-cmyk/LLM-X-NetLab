"""Multi-modal gateway & input processing (poster block 2).

Real: word tokenizer + vocabulary over the KB corpus, input normaliser.
Contracts: media encoders (image/audio) — a media input is described and
fingerprinted, never decoded; there is no media stack in this lab.
"""
import hashlib
import re

_WORD = re.compile(r"[a-z0-9']+")


def tokenize(text):
    return _WORD.findall(text.lower())


class Vocabulary:
    """Tokenizer + vocab built from a corpus (the poster's TOKENIZER box)."""

    def __init__(self, corpus):
        self.tokens = tokenize(corpus)
        self.vocab = sorted(set(self.tokens))
        self.index = {w: i for i, w in enumerate(self.vocab)}

    def encode(self, text):
        return [self.index[t] for t in tokenize(text) if t in self.index]

    def __len__(self):
        return len(self.vocab)


def describe_media(kind, data: bytes):
    """Media-encoder contract: fingerprint + size, no decoding."""
    if kind not in ("image", "audio"):
        raise ValueError(f"unsupported media kind: {kind}")
    return {
        "kind": kind,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "decoded": False,
        "note": "media encoders (CLIP/BERT-style) are contracts in this lab; bytes are fingerprinted, never decoded",
    }
