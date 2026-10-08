"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs

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
    }
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


def main() -> None:
    songs = load_songs("data/songs.csv")

    for name, user_prefs in profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, recommendations)


if __name__ == "__main__":
    main()
