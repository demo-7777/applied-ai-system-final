"""
Agentic self-critique loop (stretch feature).

A deterministic plan -> act -> critique decision chain wrapped around the core
recommender. Instead of trusting the first ranked list, the agent inspects its
own output against reliability rules, revises it, and re-checks until the list
is clean or it runs out of iterations. Every step is recorded as a reasoning
trace so the decision chain is auditable (saved to assets/agent_trace.md and
linked from ai_interactions.md).

Rules the agent enforces on its own output:
  1. Drop weak picks       — confidence below LOW_CONFIDENCE_THRESHOLD.
  2. Diversify             — penalize a second song from an already-used artist.

Run:  python -m src.agent
"""

import logging
from typing import Dict, List, Tuple

from src.recommender import (
    score_song,
    confidence,
    recommend_songs,
    LOW_CONFIDENCE_THRESHOLD,
)

logger = logging.getLogger("agent")

Rec = Tuple[Dict, float, float, str]  # (song, score, confidence, explanation)

ARTIST_PENALTY = 1.0  # points subtracted per repeat of an already-selected artist


def critique(selection: List[Rec]) -> List[str]:
    """Inspect a recommendation list and return a list of reliability issues."""
    issues: List[str] = []

    for song, _, conf, _ in selection:
        if conf < LOW_CONFIDENCE_THRESHOLD:
            issues.append(
                f"weak pick: '{song['title']}' confidence {conf:.2f} "
                f"< {LOW_CONFIDENCE_THRESHOLD}"
            )

    counts: Dict[str, int] = {}
    for song, _, _, _ in selection:
        counts[song["artist"]] = counts.get(song["artist"], 0) + 1
    for artist, n in counts.items():
        if n > 1:
            issues.append(f"low diversity: artist '{artist}' appears {n} times")

    return issues


def act(profile: Dict, songs: List[Dict], k: int) -> List[Rec]:
    """
    Revise the list: greedily select up to k songs, skipping picks below the
    confidence floor and penalizing repeated artists (diversity). May return
    fewer than k if not enough confident songs exist — an honest guardrail
    outcome rather than padding the list with junk.
    """
    scored: List[Rec] = []
    for song in songs:
        raw, reasons = score_song(profile, song)
        scored.append((song, raw, confidence(raw), "; ".join(reasons)))

    selected: List[Rec] = []
    used_artists: Dict[str, int] = {}
    pool = list(scored)

    while len(selected) < k and pool:
        best = None
        best_adj = None
        for item in pool:
            song, raw, conf, _ = item
            if conf < LOW_CONFIDENCE_THRESHOLD:
                continue  # guardrail: never re-add a weak pick
            adjusted = raw - ARTIST_PENALTY * used_artists.get(song["artist"], 0)
            if best is None or adjusted > best_adj:
                best, best_adj = item, adjusted
        if best is None:
            break  # nothing confident left
        pool.remove(best)
        selected.append(best)
        used_artists[best[0]["artist"]] = used_artists.get(best[0]["artist"], 0) + 1

    return selected


def run_agent(profile: Dict, songs: List[Dict], k: int = 5, max_iters: int = 3):
    """
    Plan -> critique -> act loop. Returns (final_selection, trace) where trace
    is a list of step dicts recording the decision chain.
    """
    trace: List[Dict] = []

    # PLAN: start from the naive baseline ranking.
    selection = recommend_songs(profile, songs, k)
    trace.append({"step": "PLAN", "detail": "baseline top-k ranking",
                  "picks": [s[0]["title"] for s in selection]})

    for i in range(1, max_iters + 1):
        issues = critique(selection)
        trace.append({"step": f"CRITIQUE #{i}", "issues": issues})
        if not issues:
            trace.append({"step": "DONE", "detail": "no issues — list accepted"})
            break
        before = [s[0]["title"] for s in selection]
        selection = act(profile, songs, k)
        after = [s[0]["title"] for s in selection]
        trace.append({"step": f"ACT #{i}", "detail": "dropped weak picks + diversified",
                      "picks": after})
        if after == before:
            # Convergence: the remaining issues are soft (e.g. a strong-genre
            # artist that survives the diversity penalty). Best effort reached.
            trace.append({"step": "CONVERGED",
                          "detail": "ACT made no change — remaining issues are best-effort only"})
            break
    else:
        trace.append({"step": "STOP", "detail": f"max_iters={max_iters} reached"})

    return selection, trace


def format_trace(name: str, profile: Dict, selection, trace) -> str:
    """Render one profile's run as a markdown reasoning trace."""
    lines = [f"### {name} — `{profile}`", ""]
    for step in trace:
        head = f"- **{step['step']}**"
        if "detail" in step:
            head += f": {step['detail']}"
        lines.append(head)
        if step.get("picks"):
            lines.append(f"  - picks: {', '.join(step['picks'])}")
        if "issues" in step:
            if step["issues"]:
                for issue in step["issues"]:
                    lines.append(f"  - ⚠ {issue}")
            else:
                lines.append("  - ✓ clean")
    lines.append("")
    lines.append("**Final list:**")
    for song, score, conf, _ in selection:
        lines.append(f"- {song['title']} — score {score:.2f}, confidence {conf:.2f}")
    lines.append("")
    return "\n".join(lines)


# Profiles chosen to exercise the loop: the Chill Lofi baseline pulls in a
# wrong-genre, energy-only pick that the agent should drop.
DEMO_PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35},
}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    from src.recommender import load_songs

    songs = load_songs("data/songs.csv")
    print("# Agentic Self-Critique Loop — Reasoning Traces\n")
    for name, profile in DEMO_PROFILES.items():
        selection, trace = run_agent(profile, songs, k=5)
        print(format_trace(name, profile, selection, trace))


if __name__ == "__main__":
    main()
