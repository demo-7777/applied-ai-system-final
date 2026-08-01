"""
Tests for the reliability/testing AI feature: confidence scoring, guardrails,
and the evaluation harness. Complements tests/test_recommender.py.
"""

import csv

import pytest

from src.recommender import (
    confidence,
    recommend_songs,
    load_songs,
    MAX_SCORE,
    LOW_CONFIDENCE_THRESHOLD,
)
from src.evaluate import evaluate, to_markdown


SAMPLE_SONGS = [
    {"id": 1, "title": "Pop Hit", "artist": "A", "genre": "pop", "mood": "happy",
     "energy": 0.8, "tempo_bpm": 120, "valence": 0.9, "danceability": 0.8, "acousticness": 0.2},
    {"id": 2, "title": "Lofi Loop", "artist": "B", "genre": "lofi", "mood": "chill",
     "energy": 0.4, "tempo_bpm": 80, "valence": 0.6, "danceability": 0.5, "acousticness": 0.9},
]


def test_confidence_is_bounded_0_to_1():
    assert confidence(MAX_SCORE) == 1.0
    assert confidence(0.0) == 0.0
    assert confidence(-5.0) == 0.0          # clamped low
    assert confidence(MAX_SCORE * 2) == 1.0  # clamped high


def test_confidence_matches_score_ratio():
    assert confidence(2.0) == pytest.approx(0.5)


def test_perfect_match_gets_high_confidence():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    top = recommend_songs(prefs, SAMPLE_SONGS, k=1)
    song, score, conf, _ = top[0]
    assert song["title"] == "Pop Hit"
    assert conf >= LOW_CONFIDENCE_THRESHOLD


def test_unknown_profile_gets_low_confidence():
    prefs = {"genre": "polka", "mood": "party", "energy": 0.5}
    top = recommend_songs(prefs, SAMPLE_SONGS, k=1)
    _, _, conf, _ = top[0]
    assert conf < LOW_CONFIDENCE_THRESHOLD


def test_empty_catalog_guardrail_raises():
    with pytest.raises(ValueError):
        recommend_songs({"genre": "pop"}, [], k=3)


def test_load_songs_skips_malformed_rows(tmp_path):
    csv_path = tmp_path / "songs.csv"
    header = "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness"
    good = "1,Good,A,pop,happy,0.8,120,0.9,0.8,0.2"
    bad = "2,Bad,B,pop,happy,NOT_A_NUMBER,120,0.9,0.8,0.2"
    csv_path.write_text("\n".join([header, good, bad]) + "\n", encoding="utf-8")

    songs = load_songs(str(csv_path))
    assert len(songs) == 1          # malformed row skipped, not crashed
    assert songs[0]["title"] == "Good"


def test_load_songs_all_malformed_raises(tmp_path):
    csv_path = tmp_path / "empty.csv"
    header = "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness"
    csv_path.write_text(header + "\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_songs(str(csv_path))


def test_evaluation_harness_reports_all_pass():
    report = evaluate(SAMPLE_SONGS + [
        {"id": 3, "title": "Jazz Night", "artist": "C", "genre": "jazz", "mood": "relaxed",
         "energy": 0.4, "tempo_bpm": 90, "valence": 0.5, "danceability": 0.4, "acousticness": 0.6},
        {"id": 4, "title": "Rock On", "artist": "D", "genre": "rock", "mood": "intense",
         "energy": 0.85, "tempo_bpm": 150, "valence": 0.4, "danceability": 0.6, "acousticness": 0.1},
    ])
    assert report["total"] == 5
    assert report["passed"] == report["total"]
    assert 0.0 <= report["avg_confidence"] <= 1.0
    assert "PASS" in to_markdown(report)
