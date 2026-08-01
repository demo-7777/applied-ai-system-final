"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import logging

from src.recommender import load_songs, recommend_songs, LOW_CONFIDENCE_THRESHOLD

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")


# Diverse taste profiles for stress testing the recommender.
PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Deep Intense Rock": {"genre": "hard rock", "mood": "intense", "energy": 0.85},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35},
}


def main() -> None:
    songs = load_songs("data/songs.csv")

    for name, user_prefs in PROFILES.items():
        print(f"\n=== {name}: {user_prefs} ===\n")
        for song, score, conf, explanation in recommend_songs(user_prefs, songs, k=5):
            flag = "  ⚠ LOW CONFIDENCE" if conf < LOW_CONFIDENCE_THRESHOLD else ""
            print(f"{song['title']} - Score: {score:.2f} - Confidence: {conf:.2f}{flag}")
            print(f"Because: {explanation}")
            print()


if __name__ == "__main__":
    main()
