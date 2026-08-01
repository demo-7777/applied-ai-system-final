"""
RAG (Retrieval-Augmented Generation) enhancement — stretch feature.

A dependency-free retriever over a small knowledge base of genre/mood "liner
notes" (data/knowledge/*.md). Before explaining a recommendation, the system
RETRIEVES the most relevant note and COMPOSES its explanation from that
retrieved text — so the retrieved data actively shapes the output rather than
being printed alongside a canned answer.

Retrieval is TF cosine similarity over bag-of-words vectors (pure Python).

Run:  python -m src.rag
"""

import glob
import math
import os
import re
import logging
from collections import Counter
from typing import Dict, List, Tuple

from src.recommender import score_song

logger = logging.getLogger("rag")

_TOKEN = re.compile(r"[a-z0-9]+")
# Very common words carry no retrieval signal; drop them so genre/mood terms win.
_STOP = {
    "the", "and", "a", "an", "to", "of", "is", "are", "it", "its", "for", "with",
    "on", "at", "or", "as", "from", "that", "this", "than", "near", "up", "in",
    "how", "they", "not", "want", "feel", "feels", "rather", "which", "keeps",
    "makes", "usually", "about", "across", "best", "good", "so", "while",
}


def _tokens(text: str) -> List[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]


class Retriever:
    """Loads knowledge docs and retrieves the most relevant ones for a query."""

    def __init__(self, docs: Dict[str, str]):
        if not docs:
            raise ValueError("Retriever requires at least one knowledge document")
        self.names = list(docs.keys())
        self.texts = docs
        self.vectors = {name: Counter(_tokens(text)) for name, text in docs.items()}

    @classmethod
    def from_dir(cls, path: str) -> "Retriever":
        docs: Dict[str, str] = {}
        for fp in sorted(glob.glob(os.path.join(path, "*.md"))):
            with open(fp, encoding="utf-8") as f:
                docs[os.path.basename(fp)] = f.read()
        logger.info("Loaded %d knowledge docs from %s", len(docs), path)
        return cls(docs)

    @staticmethod
    def _cosine(a: Counter, b: Counter) -> float:
        if not a or not b:
            return 0.0
        common = set(a) & set(b)
        dot = sum(a[t] * b[t] for t in common)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def retrieve(self, query: str, k: int = 1) -> List[Tuple[str, float]]:
        """Return the top-k (doc_name, similarity) pairs, highest first."""
        qv = Counter(_tokens(query))
        ranked = [(name, self._cosine(qv, self.vectors[name])) for name in self.names]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:k]

    def snippet(self, doc_name: str, sentences: int = 1) -> str:
        """Return the first `sentences` sentences of a doc (skipping its heading)."""
        body = re.sub(r"^#.*$", "", self.texts[doc_name], flags=re.MULTILINE).strip()
        parts = re.split(r"(?<=[.!?])\s+", body)
        return " ".join(parts[:sentences]).strip()


def _query_for(profile: Dict, song: Dict) -> str:
    """Build the retrieval query from the song and the listener's profile."""
    energy = profile.get("energy", song.get("energy", 0.5))
    level = "high energy" if energy >= 0.6 else "low energy relaxed calm"
    return " ".join([
        song.get("genre", ""), song.get("mood", ""),
        profile.get("genre", ""), profile.get("mood", ""), level,
    ])


def grounded_explanation(profile: Dict, song: Dict, retriever: Retriever) -> Dict:
    """
    RAG core: retrieve the most relevant note, then COMPOSE the explanation from
    it. Returns a dict with the base score reasons, the retrieved doc, and the
    grounded natural-language explanation.
    """
    score, reasons = score_song(profile, song)
    top = retriever.retrieve(_query_for(profile, song), k=1)
    doc_name, sim = top[0]
    context = retriever.snippet(doc_name, sentences=1)

    # The retrieved text is woven INTO the answer, not appended as a separate blob.
    grounded = (
        f"{song['title']} fits your profile because {context.lower()} "
        f"Concretely: {'; '.join(reasons)}."
    )
    return {
        "song": song["title"],
        "score": round(score, 2),
        "retrieved_doc": doc_name,
        "similarity": round(sim, 3),
        "explanation": grounded,
    }


DEMO_PROFILES = {
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35},
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    from src.recommender import load_songs, recommend_songs

    retriever = Retriever.from_dir("data/knowledge")
    songs = load_songs("data/songs.csv")

    print("# RAG-Grounded Explanations — Before / After\n")
    for name, profile in DEMO_PROFILES.items():
        song = recommend_songs(profile, songs, k=1)[0][0]
        base_reasons = score_song(profile, song)[1]
        g = grounded_explanation(profile, song, retriever)
        print(f"## {name} — top pick: {song['title']}")
        print(f"- **Baseline explanation:** {'; '.join(base_reasons)}")
        print(f"- **Retrieved doc:** {g['retrieved_doc']} (similarity {g['similarity']})")
        print(f"- **RAG explanation:** {g['explanation']}\n")


if __name__ == "__main__":
    main()
