"""
Reliability evaluation harness for the Music Recommender.

Runs the recommender against a set of labeled profiles, each with an expected
genre for its top recommendation, and reports accuracy plus average confidence.
This is the reliability/testing AI feature: it measures whether the system's
top pick actually matches the taste profile, and flags low-confidence results.

Run:  python -m src.evaluate
"""

import json
import logging

from src.recommender import load_songs, recommend_songs, LOW_CONFIDENCE_THRESHOLD

logger = logging.getLogger("evaluate")

# Labeled evaluation cases: (name, profile, expected genre of the #1 pick).
EVAL_CASES = [
    ("High-Energy Pop", {"genre": "pop", "mood": "happy", "energy": 0.8}, "pop"),
    ("Deep Intense Rock", {"genre": "rock", "mood": "intense", "energy": 0.85}, "rock"),
    ("Chill Lofi", {"genre": "lofi", "mood": "chill", "energy": 0.35}, "lofi"),
    ("Relaxed Jazz", {"genre": "jazz", "mood": "relaxed", "energy": 0.4}, "jazz"),
    # Adversarial case: genre not in the catalog -> expect low confidence.
    ("Unknown Genre", {"genre": "polka", "mood": "party", "energy": 0.5}, None),
]


def evaluate(songs) -> dict:
    """Score every case and return a structured results dict."""
    results = []
    passed = 0
    confidences = []

    for name, profile, expected_genre in EVAL_CASES:
        top = recommend_songs(profile, songs, k=1)
        song, score, conf, _ = top[0]
        confidences.append(conf)

        if expected_genre is None:
            # Guardrail case: "pass" means the system correctly flags low confidence.
            ok = conf < LOW_CONFIDENCE_THRESHOLD
            criterion = f"flag low confidence (<{LOW_CONFIDENCE_THRESHOLD})"
        else:
            ok = song["genre"] == expected_genre
            criterion = f"top pick genre == {expected_genre}"

        passed += int(ok)
        results.append({
            "case": name,
            "profile": profile,
            "criterion": criterion,
            "top_pick": song["title"],
            "top_genre": song["genre"],
            "confidence": round(conf, 2),
            "result": "PASS" if ok else "FAIL",
        })

    return {
        "total": len(EVAL_CASES),
        "passed": passed,
        "avg_confidence": round(sum(confidences) / len(confidences), 2),
        "cases": results,
    }


def to_markdown(report: dict) -> str:
    """Render the report as a parseable markdown table + summary line."""
    lines = [
        "| Case | Criterion | Top Pick | Confidence | Result |",
        "|------|-----------|----------|------------|--------|",
    ]
    for c in report["cases"]:
        lines.append(
            f"| {c['case']} | {c['criterion']} | {c['top_pick']} "
            f"({c['top_genre']}) | {c['confidence']:.2f} | {c['result']} |"
        )
    lines.append("")
    lines.append(
        f"**{report['passed']}/{report['total']} cases passed; "
        f"average confidence {report['avg_confidence']:.2f}.**"
    )
    return "\n".join(lines)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    songs = load_songs("data/songs.csv")
    report = evaluate(songs)
    print("\n" + to_markdown(report) + "\n")
    print("JSON:", json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
