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


def main() -> None:
    songs = load_songs("data/songs.csv")

    for name, user_prefs in profiles.items():
        print(f"\n=== Top recommendations for {name} ===\n")
        recommendations = recommend_songs(user_prefs, songs, k=5)
        for rec in recommendations:
            # You decide the structure of each returned item.
            # A common pattern is: (song, score, explanation)
            song, score, explanation = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {explanation}")
            print()


if __name__ == "__main__":
    main()
