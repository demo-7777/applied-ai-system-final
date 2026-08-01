"""
Tests for the agentic self-critique loop (src/agent.py).
"""

from src.agent import critique, act, run_agent
from src.recommender import LOW_CONFIDENCE_THRESHOLD


SONGS = [
    {"id": 1, "title": "Lofi A", "artist": "Room", "genre": "lofi", "mood": "chill",
     "energy": 0.35, "tempo_bpm": 80, "valence": 0.6, "danceability": 0.5, "acousticness": 0.9},
    {"id": 2, "title": "Lofi B", "artist": "Room", "genre": "lofi", "mood": "chill",
     "energy": 0.36, "tempo_bpm": 82, "valence": 0.6, "danceability": 0.5, "acousticness": 0.9},
    {"id": 3, "title": "Lofi C", "artist": "Other", "genre": "lofi", "mood": "chill",
     "energy": 0.34, "tempo_bpm": 78, "valence": 0.6, "danceability": 0.5, "acousticness": 0.9},
    # Wrong-genre, right-energy song: an energy-only "leak" pick.
    {"id": 4, "title": "Rock Ballad", "artist": "Band", "genre": "rock", "mood": "moody",
     "energy": 0.35, "tempo_bpm": 90, "valence": 0.3, "danceability": 0.4, "acousticness": 0.2},
]
LOFI_PROFILE = {"genre": "lofi", "mood": "chill", "energy": 0.35}


def test_critique_flags_weak_pick():
    # A wrong-genre song scores only on energy -> low confidence -> flagged.
    weak = [(SONGS[3], 1.0, 0.25, "energy only")]
    issues = critique(weak)
    assert any("weak pick" in i for i in issues)


def test_critique_flags_duplicate_artist():
    dup = [
        (SONGS[0], 4.0, 1.0, ""),
        (SONGS[1], 3.9, 0.98, ""),  # same artist "Room"
    ]
    issues = critique(dup)
    assert any("low diversity" in i for i in issues)


def test_act_drops_below_confidence_floor():
    selection = act(LOFI_PROFILE, SONGS, k=5)
    # The rock ballad (energy-only, low confidence) must not survive.
    titles = [s[0]["title"] for s in selection]
    assert "Rock Ballad" not in titles
    for _, _, conf, _ in selection:
        assert conf >= LOW_CONFIDENCE_THRESHOLD


def test_run_agent_improves_over_baseline():
    final, trace = run_agent(LOFI_PROFILE, SONGS, k=5, max_iters=3)
    titles = [s[0]["title"] for s in final]
    assert "Rock Ballad" not in titles           # weak pick removed
    steps = [t["step"] for t in trace]
    assert steps[0] == "PLAN"
    assert any(s.startswith("CRITIQUE") for s in steps)
    # The loop must terminate cleanly, never silently hit the raw max_iters wall.
    assert steps[-1] in ("DONE", "CONVERGED", "STOP")


def test_run_agent_terminates_without_churn():
    # With a clean, diverse catalog the loop should finish in one critique.
    clean = [SONGS[0], SONGS[2]]  # two lofi songs, different artists
    _, trace = run_agent(LOFI_PROFILE, clean, k=2, max_iters=3)
    assert trace[-1]["step"] == "DONE"
