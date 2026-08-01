"""
Specialization / "fine-tuning" enhancement — stretch feature.

Without a hosted model to fine-tune, this demonstrates specialized model
BEHAVIOR the way few-shot prompting does: a fixed persona plus a handful of
exemplars ("few-shot patterns") constrain every output to one consistent
tone/style. Here the persona is NOVA, a late-night radio DJ.

Crucially, the specialized output is shown to MEASURABLY DIFFER from the
baseline explanation via style metrics (see `compare`), not just asserted.

Run:  python -m src.specialize
"""

import logging
import re
from typing import Dict, List

from src.recommender import score_song

logger = logging.getLogger("specialize")

PERSONA = "NOVA (late-night DJ)"

# Few-shot exemplars: each pins the DJ tone for one (mood-bucket, energy-bucket).
# The generator selects the closest exemplar and fills it — the same way a
# few-shot prompt conditions a model's style from examples.
FEWSHOT: List[Dict] = [
    {"mood": "chill", "energy": "low",
     "line": "Easy now — slide into {title} by {artist} and let the {genre} haze carry you."},
    {"mood": "relaxed", "energy": "low",
     "line": "Keep it mellow — {title} by {artist} is that warm {genre} glow for the quiet hours."},
    {"mood": "happy", "energy": "high",
     "line": "Turn it UP — {title} by {artist} is pure {genre} sunshine, hands in the air!"},
    {"mood": "intense", "energy": "high",
     "line": "Brace yourself — {title} by {artist} hits with full {genre} force. No brakes!"},
    {"mood": "romantic", "energy": "low",
     "line": "Dim the lights — {title} by {artist} brings the slow {genre} feeling in close."},
]
# Vocabulary that marks the DJ persona (used to MEASURE specialization).
PERSONA_MARKERS = {
    "up", "now", "easy", "brace", "hands", "air", "haze", "turn", "dim", "lights",
    "glow", "mellow", "slide", "brakes", "carry", "force", "sunshine", "warm",
    "quiet", "hours", "slow", "keep",
}

_ENERGY_HI = 0.6


def _bucket(energy: float) -> str:
    return "high" if energy >= _ENERGY_HI else "low"


def _pick_exemplar(mood: str, energy: float) -> Dict:
    """Select the few-shot exemplar closest to the song's mood/energy bucket."""
    eb = _bucket(energy)
    for ex in FEWSHOT:
        if ex["mood"] == mood and ex["energy"] == eb:
            return ex
    # Fall back to any exemplar in the same energy bucket, else the first.
    for ex in FEWSHOT:
        if ex["energy"] == eb:
            return ex
    return FEWSHOT[0]


def specialized_blurb(song: Dict) -> str:
    """Generate a DJ-persona, constrained-tone blurb for a song."""
    ex = _pick_exemplar(song.get("mood", ""), song.get("energy", 0.5))
    return ex["line"].format(
        title=song.get("title", "this track"),
        artist=song.get("artist", "a mystery artist"),
        genre=song.get("genre", "music"),
    )


def baseline_blurb(profile: Dict, song: Dict) -> str:
    """The plain, un-styled explanation used as the comparison baseline."""
    _, reasons = score_song(profile, song)
    return "; ".join(reasons)


def style_metrics(text: str) -> Dict:
    """Measure stylistic markers so specialization can be quantified."""
    words = re.findall(r"[a-z']+", text.lower())
    return {
        "direct_address": sum(w in ("you", "your", "yourself") for w in words),
        "exclamations": text.count("!"),
        "persona_markers": sum(w in PERSONA_MARKERS for w in words),
        # A single "specialization score" combining the style signals.
        "style_score": (
            2 * sum(w in PERSONA_MARKERS for w in words)
            + text.count("!")
            + sum(w in ("you", "your") for w in words)
        ),
    }


def compare(profile: Dict, song: Dict) -> Dict:
    """Return baseline vs specialized text with metrics and a difference verdict."""
    base = baseline_blurb(profile, song)
    spec = specialized_blurb(song)
    bm, sm = style_metrics(base), style_metrics(spec)
    return {
        "song": song["title"],
        "baseline": base,
        "specialized": spec,
        "baseline_style_score": bm["style_score"],
        "specialized_style_score": sm["style_score"],
        "measurably_different": sm["style_score"] > bm["style_score"],
    }


DEMO_PROFILES = {
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35},
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.85},
}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    from src.recommender import load_songs, recommend_songs

    songs = load_songs("data/songs.csv")
    print(f"# Specialized Output — persona: {PERSONA}\n")
    print("| Profile | Baseline style score | Specialized style score | Differs? |")
    print("|---------|----------------------|-------------------------|----------|")
    details = []
    for name, profile in DEMO_PROFILES.items():
        song = recommend_songs(profile, songs, k=1)[0][0]
        c = compare(profile, song)
        print(f"| {name} | {c['baseline_style_score']} | {c['specialized_style_score']} "
              f"| {'YES' if c['measurably_different'] else 'no'} |")
        details.append((name, c))
    print()
    for name, c in details:
        print(f"### {name} — {c['song']}")
        print(f"- Baseline:    {c['baseline']}")
        print(f"- Specialized: {c['specialized']}\n")


if __name__ == "__main__":
    main()
