"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import argparse

from recommender import DEFAULT_STRATEGY, STRATEGIES, load_songs, recommend_songs

# Ranking mode. Change this, or pass --strategy on the command line.
# Options: balanced (default), classic, genre_first, mood_first, energy_focused
# (or "all" on the command line to compare every mode).
STRATEGY = DEFAULT_STRATEGY

profiles = {
    "my_taste": {
        "favorite_genres": {"hip-hop", "rap", "trap"},
        "favorite_moods": {"reflective", "melancholic"},
        "target_energy": 0.50,
        "target_valence": 0.50,
        "target_acousticness": 0.35
    },

    "high_energy": {
        "favorite_genres": {"EDM", "metal", "trap"},
        "favorite_moods": {"aggressive", "uplifting"},
        "target_energy": 0.95,
        "target_valence": 0.80,
        "target_acousticness": 0.05
    },

    "low_energy": {
        "favorite_genres": {"classical", "ambient", "lofi"},
        "favorite_moods": {"dreamy", "chill"},
        "target_energy": 0.20,
        "target_valence": 0.30,
        "target_acousticness": 0.90
    },

    "happy_pop": {
        "favorite_genres": {"pop"},
        "favorite_moods": {"happy"},
        "target_energy": 0.80,
        "target_valence": 0.80,
        "target_acousticness": 0.20
    }
}


user_profiles = {
    "Reflective Hip-Hop": {
        "favorite_genres": {"hip-hop", "rap", "trap"},
        "favorite_moods": {"reflective", "melancholic"},
        "target_energy": 0.50,
        "target_valence": 0.50,
        "target_acousticness": 0.35
    },

    "High-Energy Workout": {
        "favorite_genres": {"pop", "EDM", "metal"},
        "favorite_moods": {"intense", "uplifting", "aggressive"},
        "target_energy": 0.95,
        "target_valence": 0.80,
        "target_acousticness": 0.05
    },

    "Chill Lofi": {
        "favorite_genres": {"lofi", "ambient", "classical"},
        "favorite_moods": {"chill", "dreamy", "relaxed"},
        "target_energy": 0.25,
        "target_valence": 0.45,
        "target_acousticness": 0.90
    }
}


adversarial_profiles = {
    # Conflicting: high energy + sad mood
    "Sad Banger": {
        "favorite_genres": {"EDM"},
        "favorite_moods": {"melancholic", "reflective"},
        "target_energy": 0.95,
        "target_valence": 0.10,
        "target_acousticness": 0.05
    },

    # Conflicting: calm acoustic genres but max energy
    "Calm Genre, Max Energy": {
        "favorite_genres": {"classical", "ambient"},
        "favorite_moods": {"chill", "dreamy"},
        "target_energy": 1.0,
        "target_valence": 0.5,
        "target_acousticness": 0.95
    },

    # A genre match should not beat a perfect mood + energy fit
    "Genre Trap": {
        "favorite_genres": {"metal"},
        "favorite_moods": {"chill", "relaxed"},
        "target_energy": 0.20,
        "target_valence": 0.5,
        "target_acousticness": 0.9
    },

    # Out-of-range energy: can the score go negative?
    "Impossible Energy": {
        "favorite_genres": {"pop"},
        "favorite_moods": {"happy"},
        "target_energy": -1.0,
        "target_valence": 0.5,
        "target_acousticness": 0.5
    },

    # Case mismatch: dataset has 'EDM' and 'R&B' but 'hip-hop'
    "Wrong Case": {
        "favorite_genres": {"edm", "r&b", "Hip-Hop"},
        "favorite_moods": {"Happy", "CHILL"},
        "target_energy": 0.7,
        "target_valence": 0.5,
        "target_acousticness": 0.5
    },

    # Genres and moods that are not in the dataset
    "Unknown Tastes": {
        "favorite_genres": {"k-pop", "bossa nova"},
        "favorite_moods": {"nostalgic"},
        "target_energy": 0.5,
        "target_valence": 0.5,
        "target_acousticness": 0.5
    },

    # Lists every genre and mood
    "Likes Everything": {
        "favorite_genres": {"pop", "lofi", "rock", "ambient", "jazz", "synthwave",
                            "indie pop", "hip-hop", "rap", "trap", "R&B", "disco",
                            "EDM", "classical", "metal"},
        "favorite_moods": {"chill", "happy", "intense", "relaxed", "moody", "focused",
                           "melancholic", "reflective", "aggressive", "romantic",
                           "playful", "uplifting", "dreamy", "ominous"},
        "target_energy": 0.5,
        "target_valence": 0.5,
        "target_acousticness": 0.5
    },

    # Empty sets hit the favorite_genre fallback in score_song
    "Empty Prefs": {
        "favorite_genres": set(),
        "favorite_moods": set(),
        "target_energy": 0.5,
        "target_valence": 0.5,
        "target_acousticness": 0.5
    },

    # Dead-center energy: many songs tie, so tie-breaking decides
    "Dead Center": {
        "favorite_genres": {"jazz"},
        "favorite_moods": {"relaxed"},
        "target_energy": 0.5,
        "target_valence": 0.5,
        "target_acousticness": 0.5
    },
}


WIDTH = 64
MAX_SCORE = 4.0


def print_recommendations(name: str, recommendations: list) -> None:
    """Print one profile's ranked recommendations with the reasons for each."""
    print("\n" + "=" * WIDTH)
    print(f" Top {len(recommendations)} recommendations for: {name}")
    print("=" * WIDTH)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']}  by {song['artist']}")
        print(f"   Score: {score:.2f} / {MAX_SCORE:.2f}")
        print("   Why:")
        for reason in explanation.split("; "):
            print(f"     - {reason}")

    print("\n" + "-" * WIDTH)


def run_strategy(strategy: str, songs: list) -> None:
    """Print every profile's top 5 under one ranking strategy."""
    weights = ", ".join(f"{k} {v:g}" for k, v in STRATEGIES[strategy].items() if v)
    print(f"\n##### Strategy: {strategy} ({weights}) #####")

    for name, user_prefs in {**profiles, **adversarial_profiles}.items():
        try:
            recommendations = recommend_songs(user_prefs, songs, k=5, strategy=strategy)
        except Exception as error:
            print("\n" + "=" * WIDTH)
            print(f" {name}: FAILED with {type(error).__name__}: {error}")
            print("=" * WIDTH)
            continue
        print_recommendations(name, recommendations)


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument(
        "--strategy",
        default=STRATEGY,
        choices=[*STRATEGIES, "all"],
        help="ranking mode (default: %(default)s); 'all' runs every mode",
    )
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    for strategy in STRATEGIES if args.strategy == "all" else [args.strategy]:
        run_strategy(strategy, songs)


if __name__ == "__main__":
    main()
