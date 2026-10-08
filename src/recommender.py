import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

GENRE_POINTS = 2.0
MOOD_POINTS = 1.0

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

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs from a CSV file into dicts, converting numeric columns to int/float."""
    int_fields = ("id", "tempo_bpm")
    float_fields = ("energy", "valence", "danceability", "acousticness")

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song (max 4.0) and return the score with human-readable reasons."""
    genres = user_prefs.get("favorite_genres") or {user_prefs["favorite_genre"]}
    moods = user_prefs.get("favorite_moods") or {user_prefs["favorite_mood"]}

    score = 0.0
    reasons: List[str] = []

    if song["genre"] in genres:
        score += GENRE_POINTS
        reasons.append(f"genre match: {song['genre']} (+{GENRE_POINTS:.1f})")

    if song["mood"] in moods:
        score += MOOD_POINTS
        reasons.append(f"mood match: {song['mood']} (+{MOOD_POINTS:.1f})")

    energy_points = 1.0 - abs(song["energy"] - user_prefs["target_energy"])
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs target "
        f"{user_prefs['target_energy']:.2f} (+{energy_points:.2f})"
    )

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Return the top k (song, score, explanation) tuples, highest score first."""
    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]
    ranked = sorted(
        scored,
        key=lambda item: (
            -item[1],
            abs(item[0]["energy"] - user_prefs["target_energy"]),
            item[0]["title"],
        ),
    )
    return ranked[:k]
