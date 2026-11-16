"""Hybrid retrieval over regulation chunks: BM25 (keywords) + LSA embeddings (meaning), fused with RRF.

- BM25 is strong when the question uses the regulation's own words ("register of information").
- LSA embeddings (TF-IDF compressed with SVD) catch paraphrases ("list of our cloud vendors").
- Reciprocal Rank Fusion merges the two rankings without having to calibrate their scores.
- BM25 gets more weight than LSA in the fusion: on legal text, exact terms matter more than loose meaning.
- If the best keyword match is weak, we refuse instead of guessing. (Dense similarity alone is a poor
  refusal signal: an off-topic question with one known word can still score high.)
"""
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

CHUNKS = Path("data/processed/chunks.jsonl")
TOKEN = re.compile(r"[a-z0-9]+")
STOP = set("the of and to in a or for be shall by that with as on is are which any this their its an at from it not where".split())

# Domain synonyms bridge the gap between how PMs talk and how regulators write.
SYNONYMS = {
    "vendor": "third-party provider", "vendors": "third-party providers", "supplier": "third-party provider",
    "cloud": "ict third-party service provider", "outage": "ict-related incident", "incident": "ict-related incident",
    "breach": "personal data breach", "pentest": "threat-led penetration testing", "dpia": "data protection impact assessment",
    "sca": "strong customer authentication", "2fa": "strong customer authentication", "fines": "administrative fines",
}


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN.findall(text.lower()) if t not in STOP]


def expand(query: str) -> str:
    extra = [v for k, v in SYNONYMS.items() if re.search(rf"\b{k}\b", query.lower())]
    return query + " " + " ".join(extra)


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs]
        self.len = np.array([len(d) for d in docs], dtype=float)
        self.avg = self.len.mean()
        df = Counter(t for d in docs for t in set(d))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, q: list[str]) -> np.ndarray:
        out = np.zeros(len(self.tf))
        for i, tf in enumerate(self.tf):
            norm = self.k1 * (1 - self.b + self.b * self.len[i] / self.avg)
            out[i] = sum(self.idf.get(t, 0) * tf[t] * (self.k1 + 1) / (tf[t] + norm) for t in q if t in tf)
        return out


@dataclass
class Hit:
    chunk: dict
    score: float      # fused RRF score (for ranking)
    dense: float      # cosine similarity (meaning)
    bm25: float       # keyword score (for the refusal decision)


class Retriever:
    def __init__(self, chunks, bm25, vectorizer, svd, dense, bm25_threshold=8.0, weights=(1.0, 0.5)):
        self.chunks, self.bm25, self.vectorizer, self.svd, self.dense = chunks, bm25, vectorizer, svd, dense
        self.bm25_threshold = bm25_threshold
        self.weights = weights  # (BM25, LSA) weight in the fusion

    @classmethod
    def build(cls, dims: int = 200) -> "Retriever":
        chunks = [json.loads(l) for l in CHUNKS.open()]
        texts = [f"{c['citation']}. {c['text']}" for c in chunks]
        bm25 = BM25([tokenize(t) for t in texts])
        vectorizer = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), min_df=2, stop_words="english")
        tfidf = vectorizer.fit_transform(texts)
        svd = TruncatedSVD(n_components=dims, random_state=0)
        dense = normalize(svd.fit_transform(tfidf))
        return cls(chunks, bm25, vectorizer, svd, dense)

    @classmethod
    def load(cls) -> "Retriever":
        # Building takes about a second for ~400 chunks, so we rebuild instead of caching to disk.
        return cls.build()

    def embed(self, text: str) -> np.ndarray:
        return normalize(self.svd.transform(self.vectorizer.transform([text])))[0]

    def search(self, query: str, k: int = 5, reg: str | None = None, rrf_k: int = 60) -> list[Hit]:
        q = expand(query)
        sparse = self.bm25.scores(tokenize(q))
        dense = self.dense @ self.embed(q)
        mask = np.array([reg is None or c["reg"] == reg for c in self.chunks])
        fused = np.zeros(len(self.chunks))
        for scores, w in zip((sparse, dense), self.weights):
            ranked = np.argsort(-np.where(mask, scores, -np.inf))
            for rank, i in enumerate(ranked[:100]):
                fused[i] += w / (rrf_k + rank + 1)
        # Keep only the best chunk per article so the top k covers k different articles.
        hits, seen = [], set()
        for i in np.argsort(-fused):
            art = (self.chunks[i]["reg"], self.chunks[i]["article"])
            if not mask[i] or art in seen:
                continue
            seen.add(art)
            hits.append(Hit(self.chunks[i], float(fused[i]), float(dense[i]), float(sparse[i])))
            if len(hits) == k:
                break
        return hits

    def answerable(self, hits: list[Hit]) -> bool:
        return bool(hits) and max(h.bm25 for h in hits) >= self.bm25_threshold


if __name__ == "__main__":
    r = Retriever.build()
    for q in ["Do we need a register of all our cloud vendors?", "How fast must we report a data breach?",
              "What is the best pizza in Gothenburg?"]:
        hits = r.search(q, k=3)
        print(f"\nQ: {q}  answerable={r.answerable(hits)}")
        for h in hits:
            print(f"  {h.chunk['citation'][:70]:70}  bm25={h.bm25:5.1f}  dense={h.dense:.2f}")
