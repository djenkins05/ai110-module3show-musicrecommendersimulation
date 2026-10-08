# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders such as Spotify's combine two broad approaches: collaborative filtering, which learns from what millions of other listeners play, skip and save, and content-based filtering, which compares the measurable characteristics of songs (genre, tempo, energy, mood) to what a listener already likes. My version is purely content-based. It has no listening history and no other users, so it can only compare a song's attributes to a single stated taste profile. It prioritizes **closeness of match** over popularity or novelty. Each song gets a score for how well it fits the user, and the highest-scoring songs are recommended. Genre carries the most weight, mood counts half as much, and energy is rewarded for being *near* the user's target, not for being high.

### Features used

**`Song`** (each row of `data/songs.csv`):

- `genre`, `mood`: categorical, used in scoring
- `energy` (0-1): numeric, used in scoring
- `tempo_bpm`, `valence`, `danceability`, `acousticness`: stored for each song and available for later experiments
- `id`, `title`, `artist`: identifiers, used for display only, not scoring

**`UserProfile`**:

- `favorite_genre`: the genre the user wants
- `favorite_mood`: the mood the user wants
- `target_energy` (0-1): the energy level the user wants
- `likes_acoustic`: whether the user prefers acoustic songs, a possible extra signal using `acousticness`

### Data flow

```mermaid
flowchart TD
    A["INPUT: User Prefs<br/>favorite_genre, favorite_mood, target_energy"] --> D
    B[("data/songs.csv")] --> C["load_songs()"] --> D
    D{"PROCESS: for each song"} --> E["score_song(user_prefs, song)"]
    E --> F["Record (song, score, reasons)"]
    F -- "next song" --> D
    D -- "all songs judged" --> G["Sort by score, descending"]
    G --> H["OUTPUT: Top K Recommendations<br/>title, score, explanation"]
```

### Algorithm Recipe

Each song is scored on its own (the **scoring rule**), then all songs are sorted and the top `k` are returned (the **ranking rule**).

| Signal | Points | Rule |
|---|---|---|
| Genre match | +2.0 | song genre equals `favorite_genre`, otherwise 0 |
| Mood match | +1.0 | song mood equals `favorite_mood`, otherwise 0 |
| Energy similarity | 0.0 to +1.0 | `1.0 - abs(song.energy - target_energy)` |

```
score = 2.0 * genre_match + 1.0 * mood_match + (1.0 - |song.energy - target_energy|)
```

- **Maximum score:** 4.0 (genre, mood and energy all match perfectly).
- **Why genre is worth double mood:** genre is a stable, coarse part of someone's taste, while mood shifts from hour to hour.
- **Why energy uses closeness:** rewarding raw energy would always favor loud songs. Closeness lets a user who wants calm music get calm songs.
- **Ranking rule:** sort by score, highest first, and break ties by smaller energy gap, then title, so results are deterministic. Return the top `k` with a plain-language reason for each (for example, "genre match (+2.0)").

### Expected biases

- **Genre can dominate.** A genre match is worth up to twice a mood match, so a song in the right genre but the wrong mood and energy can outrank a song that fits the user's mood and energy perfectly. Great mood matches in other genres may be buried.
- **Genre labels are exact-match.** "pop" and "indie pop", or "hip-hop", "rap" and "trap", count as completely different genres, so closely related songs get no credit.
- **Tiny catalog.** Most genres have only one song, so a genre match often decides the top result on its own, and users whose genre is not in the catalog get recommendations driven only by mood and energy.
- **Mood is all-or-nothing.** "chill" and "relaxed" are treated as unrelated, even though a listener would likely enjoy both.
- **Unused features.** Tempo, valence, danceability and acousticness are ignored, so two songs that feel very different can score the same.
- **Single-profile assumption.** One fixed taste profile cannot capture a listener whose preferences change by context, and there is no novelty, so the system tends to repeat the same kind of song.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



