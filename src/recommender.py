import csv
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger("recommender")

# Maximum achievable score: genre (2.0) + mood (1.0) + perfect energy match (1.0).
MAX_SCORE = 4.0
# Below this confidence, a recommendation is flagged as weak (guardrail).
LOW_CONFIDENCE_THRESHOLD = 0.4


def confidence(score: float) -> float:
    """Normalize a raw compatibility score into a 0.0-1.0 confidence value."""
    return max(0.0, min(1.0, score / MAX_SCORE))

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Compatibility score for one song: genre +2.0, mood +1.0, energy similarity 0-1."""
        score = 0.0
        if user.favorite_genre == song.genre:
            score += 2.0
        if user.favorite_mood == song.mood:
            score += 1.0
        score += 1.0 - abs(song.energy - user.target_energy)
        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs ranked by compatibility with the user profile."""
        return sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Build a human-readable explanation of why a song matches the profile."""
        reasons: List[str] = []
        if user.favorite_genre == song.genre:
            reasons.append(f"genre match: {song.genre} (+2.0)")
        if user.favorite_mood == song.mood:
            reasons.append(f"mood match: {song.mood} (+1.0)")
        energy_similarity = 1.0 - abs(song.energy - user.target_energy)
        reasons.append(f"energy close to {user.target_energy} (+{energy_similarity:.2f})")
        return f"{song.title} scored {self._score(user, song):.2f} — " + "; ".join(reasons)


        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    float_fields = {"energy", "valence", "danceability", "acousticness"}
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            try:
                row["id"] = int(row["id"])
                row["tempo_bpm"] = int(row["tempo_bpm"])
                for field in float_fields:
                    row[field] = float(row[field])
            except (ValueError, TypeError, KeyError) as err:
                # Guardrail: skip malformed rows instead of crashing the whole run.
                logger.warning("Skipping malformed row %d in %s: %s", line_no, csv_path, err)
                continue
            songs.append(row)
    if not songs:
        raise ValueError(f"No valid songs loaded from {csv_path}")
    logger.info("Loaded %d songs from %s", len(songs), csv_path)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons: List[str] = []

    if user_prefs.get("genre") == song["genre"]:
        score += 2.0
        reasons.append(f"genre match: {song['genre']} (+2.0)")

    if user_prefs.get("mood") == song["mood"]:
        score += 1.0
        reasons.append(f"mood match: {song['mood']} (+1.0)")

    if "energy" in user_prefs:
        energy_similarity = 1.0 - abs(song["energy"] - user_prefs["energy"])
        score += energy_similarity
        reasons.append(f"energy close to {user_prefs['energy']} (+{energy_similarity:.2f})")

    if not reasons:
        reasons.append("no strong matches")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Returns (song, score, confidence, explanation) tuples, ranked highest-first.
    Required by src/main.py
    """
    if not songs:
        # Guardrail: refuse to recommend from an empty catalog.
        raise ValueError("Cannot recommend from an empty song catalog")

    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, confidence(score), "; ".join(reasons)))

    # Ranking Rule: sort by score, highest first, keep the top k.
    scored.sort(key=lambda item: item[1], reverse=True)
    top = scored[:k]

    if top and top[0][2] < LOW_CONFIDENCE_THRESHOLD:
        # Guardrail: warn when even the best match is weak.
        logger.warning(
            "Low confidence (%.2f) for prefs %s — profile may not match the catalog",
            top[0][2], user_prefs,
        )
    return top
