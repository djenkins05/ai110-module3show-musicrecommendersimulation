import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import asdict, dataclass

# Ranking strategies: how many points each signal is worth.
# Every strategy's weights must sum to MAX_SCORE (4.0) in main.py.
# "balanced" is the default: no single signal outweighs the others.
# The rest are experiments. "classic" is the original formula (genre 2, mood 1,
# energy 1, and valence/acousticness ignored).
STRATEGIES: Dict[str, Dict[str, float]] = {
    "balanced":       {"genre": 1.0, "mood": 1.0, "energy": 1.0, "valence": 0.5,  "acousticness": 0.5},
    "classic":        {"genre": 2.0, "mood": 1.0, "energy": 1.0, "valence": 0.0,  "acousticness": 0.0},
    "genre_first":    {"genre": 2.5, "mood": 0.5, "energy": 0.5, "valence": 0.25, "acousticness": 0.25},
    "mood_first":     {"genre": 0.5, "mood": 2.0, "energy": 0.5, "valence": 0.75, "acousticness": 0.25},
    "energy_focused": {"genre": 0.5, "mood": 0.5, "energy": 2.0, "valence": 0.5,  "acousticness": 0.5},
}
DEFAULT_STRATEGY = "balanced"
MAX_SCORE = 4.0
CLOSENESS_FEATURES = ("energy", "valence", "acousticness")

for _name, _weights in STRATEGIES.items():
    assert abs(sum(_weights.values()) - MAX_SCORE) < 1e-9, f"{_name} weights must sum to 4.0"

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

    Uses the same scoring rules as score_song, so both interfaces agree.
    """
    def __init__(self, songs: List[Song], strategy: str = DEFAULT_STRATEGY):
        self.songs = songs
        self.strategy = strategy

    @staticmethod
    def _to_prefs(user: UserProfile) -> Dict:
        """Convert a UserProfile into the dict that score_song expects."""
        return {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            # Only used by strategies that score acousticness.
            "target_acousticness": 0.8 if user.likes_acoustic else 0.2,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs for this user, best match first."""
        song_dicts = [asdict(song) for song in self.songs]
        by_dict_id = {id(d): song for d, song in zip(song_dicts, self.songs)}
        ranked = recommend_songs(self._to_prefs(user), song_dicts, k, self.strategy)
        return [by_dict_id[id(song_dict)] for song_dict, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain a song's score in one line, e.g. "Title: 3.98 / 4.00 - genre match: pop (+2.0); ..."."""
        score, reasons = score_song(self._to_prefs(user), asdict(song), self.strategy)
        return f"{song.title}: {score:.2f} / 4.00 - " + "; ".join(reasons)

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

def _points(value: float) -> str:
    """Format a point value with one decimal, or two when needed (2.0, 0.25)."""
    text = f"{value:.2f}"
    return text[:-1] if text.endswith("0") else text

def score_song(
    user_prefs: Dict, song: Dict, strategy: str = DEFAULT_STRATEGY
) -> Tuple[float, List[str]]:
    """Score one song (max 4.0) under a ranking strategy and return the score with reasons."""
    weights = STRATEGIES[strategy]
    genres = user_prefs.get("favorite_genres") or {user_prefs["favorite_genre"]}
    moods = user_prefs.get("favorite_moods") or {user_prefs["favorite_mood"]}

    # Closeness signals are skipped when the weight is 0 or the profile has no target.
    features = [
        f for f in CLOSENESS_FEATURES
        if weights[f] and user_prefs.get(f"target_{f}") is not None
    ]
    # Rescale so the weights of the signals actually used still add up to MAX_SCORE.
    # With a full profile the scale is exactly 1.0, so nothing changes.
    scale = MAX_SCORE / (weights["genre"] + weights["mood"] + sum(weights[f] for f in features))

    score = 0.0
    reasons: List[str] = []

    if weights["genre"] and song["genre"] in genres:
        points = weights["genre"] * scale
        score += points
        reasons.append(f"genre match: {song['genre']} (+{_points(points)})")

    if weights["mood"] and song["mood"] in moods:
        points = weights["mood"] * scale
        score += points
        reasons.append(f"mood match: {song['mood']} (+{_points(points)})")

    # Full points at the exact target, fading to 0 as the gap grows.
    for feature in features:
        target = user_prefs[f"target_{feature}"]
        points = weights[feature] * scale * (1.0 - abs(song[feature] - target))
        score += points
        reasons.append(f"{feature} {song[feature]:.2f} vs target {target:.2f} (+{points:.2f})")

    return score, reasons

def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, strategy: str = DEFAULT_STRATEGY
) -> List[Tuple[Dict, float, str]]:
    """Return the top k (song, score, explanation) tuples, highest score first."""
    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song, strategy)]
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
