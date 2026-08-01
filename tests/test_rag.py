"""
Tests for the RAG enhancement (src/rag.py): retrieval relevance and grounding.
"""

import pytest

from src.rag import Retriever, grounded_explanation


DOCS = {
    "lofi.md": "# Lofi\nLofi is mellow and low-energy, great for study and calm focus.",
    "rock.md": "# Rock\nRock is loud, guitar-driven, and high-energy for workouts.",
    "jazz.md": "# Jazz\nJazz is warm, relaxed, and groove-based for dinners.",
}

SONG = {"id": 1, "title": "Test Lofi", "artist": "A", "genre": "lofi", "mood": "chill",
        "energy": 0.35, "tempo_bpm": 80, "valence": 0.6, "danceability": 0.5, "acousticness": 0.9}
PROFILE = {"genre": "lofi", "mood": "chill", "energy": 0.35}


def test_empty_knowledge_base_raises():
    with pytest.raises(ValueError):
        Retriever({})


def test_retrieve_returns_most_relevant_doc():
    r = Retriever(DOCS)
    top = r.retrieve("lofi mellow low energy study calm", k=1)
    assert top[0][0] == "lofi.md"
    assert top[0][1] > 0.0            # non-zero similarity


def test_retrieve_ranks_rock_query_to_rock_doc():
    r = Retriever(DOCS)
    assert r.retrieve("loud guitar high energy workout", k=1)[0][0] == "rock.md"


def test_similarity_is_bounded():
    r = Retriever(DOCS)
    for _, sim in r.retrieve("lofi rock jazz energy", k=3):
        assert 0.0 <= sim <= 1.0


def test_snippet_skips_heading():
    r = Retriever(DOCS)
    snip = r.snippet("lofi.md", sentences=1)
    assert not snip.startswith("#")
    assert "Lofi" in snip or "lofi" in snip.lower()


def test_grounded_explanation_uses_retrieved_text():
    r = Retriever(DOCS)
    result = grounded_explanation(PROFILE, SONG, r)
    # The retrieved doc drives the answer...
    assert result["retrieved_doc"] == "lofi.md"
    # ...and its retrieved content is woven into the explanation text.
    assert "mellow" in result["explanation"].lower()
    # ...alongside the concrete score reasons (grounding, not replacing).
    assert "genre match" in result["explanation"]
