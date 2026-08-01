"""
Tests for the specialization stretch (src/specialize.py): the persona output
must measurably differ from the baseline and stay deterministic.
"""

from src.specialize import (
    specialized_blurb,
    baseline_blurb,
    style_metrics,
    compare,
    _pick_exemplar,
)


SONG = {"id": 1, "title": "Storm Runner", "artist": "Voltline", "genre": "rock",
        "mood": "intense", "energy": 0.85, "tempo_bpm": 150, "valence": 0.4,
        "danceability": 0.6, "acousticness": 0.1}
PROFILE = {"genre": "rock", "mood": "intense", "energy": 0.85}


def test_specialized_differs_from_baseline():
    base = baseline_blurb(PROFILE, SONG)
    spec = specialized_blurb(SONG)
    assert spec != base
    assert SONG["title"] in spec and SONG["artist"] in spec


def test_specialized_style_score_exceeds_baseline():
    c = compare(PROFILE, SONG)
    assert c["measurably_different"] is True
    assert c["specialized_style_score"] > c["baseline_style_score"]


def test_baseline_has_no_persona_markers():
    # The plain explanation should read as neutral (no DJ styling leaking in).
    assert style_metrics(baseline_blurb(PROFILE, SONG))["persona_markers"] == 0


def test_specialization_is_deterministic():
    assert specialized_blurb(SONG) == specialized_blurb(SONG)


def test_exemplar_selection_matches_mood_and_energy():
    ex = _pick_exemplar("intense", 0.85)
    assert ex["mood"] == "intense" and ex["energy"] == "high"


def test_low_energy_falls_back_within_bucket():
    # An unseen mood at low energy still yields a low-energy-styled exemplar.
    ex = _pick_exemplar("sleepy", 0.2)
    assert ex["energy"] == "low"
