# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**MatchVibe 1.0**

A small music recommender that checks if a song's vibe matches what you asked for.

---

## 2. Goal / Task

MatchVibe tries to answer one question: "Which songs should this person hear next?"

It takes a taste profile. The profile has favorite genres, favorite moods, and target levels for energy, valence (how upbeat), and acousticness. It scores every song in the catalog. Then it returns the top 5 songs. Each song comes with a short reason, like "genre match: pop (+1.0)".

It does not predict what a person will like in real life. It only finds songs that match what the person typed.

---

## 3. Data Used

- **Size:** 18 songs in `data/songs.csv`.
- **Origin:** The starter file had 10 songs. I added 8 more, so I could cover hip-hop, rap, trap, R&B, disco, EDM, classical, and metal.
- **Features per song:** title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness.
- **Features the score actually uses:** genre, mood, energy, valence, and acousticness in the default `balanced` mode. Tempo and danceability are never scored. The original `classic` mode uses only genre, mood, and energy.
- **Genres:** 15 in total. 13 of them have only one song.
- **Moods:** 14 in total, like chill, happy, intense, and melancholic.
- **Limits:**
  - The catalog is tiny.
  - No song has energy between 0.55 and 0.74.
  - There is no country, Latin, K-pop, Afrobeats, folk, or reggae.
  - Two artists (LoRoom and Neon Echo) have 2 songs each.

---

## 4. Algorithm Summary

Each song gets points. The song with the most points wins.

The default mode is called **balanced**. No single signal can decide the ranking.

| Question | Points |
|---|---|
| Is the song's genre one of your favorites? | +1.0 |
| Is the song's mood one of your favorites? | +1.0 |
| How close is the song's energy to your target? | 0 to +1.0 |
| How close is the song's valence (how upbeat) to your target? | 0 to +0.5 |
| How close is the song's acousticness to your target? | 0 to +0.5 |

The best possible score is 4.0.

The "how close" points are `weight x (1 - the gap)`. A song with the exact value you want gets the full points. A song far away gets close to zero.

If a profile leaves out a target, the other weights are scaled up so the best possible score is still 4.0.

If two songs tie, the one with the closer energy goes first. If they still tie, the title decides.

### Other ranking modes

You can switch modes in `main.py` or with `--strategy`. Each mode splits the same 4 points differently. `classic` is my first formula. I kept it as an experiment. The Evaluation section below was run on the default `balanced` mode.

| Mode | Genre | Mood | Energy | Valence | Acousticness |
|---|---|---|---|---|---|
| `balanced` (default) | 1.0 | 1.0 | 1.0 | 0.5 | 0.5 |
| `classic` (original) | 2.0 | 1.0 | 1.0 | 0 | 0 |
| `genre_first` | 2.5 | 0.5 | 0.5 | 0.25 | 0.25 |
| `mood_first` | 0.5 | 2.0 | 0.5 | 0.75 | 0.25 |
| `energy_focused` | 0.5 | 0.5 | 2.0 | 0.5 | 0.5 |

`balanced` is my fix for the genre problem below. Genre is worth no more than any other signal, so a good mood and energy fit can beat a genre-only match. In the Genre Trap test, it put a calm song first instead of Enter Sandman. For Happy Pop, it moved "Rooftop Lights" above "Gym Hero". The tradeoffs of every mode are in Experiment 2 in the README.

---

## 5. Observed Behavior / Biases

These come from running `python src/main.py` in the default `balanced` mode. The full output is in the README.

### Genre no longer decides the ranking

In balanced mode, a genre match is worth 1 point. A song needs more than the right label to win.

The *Genre Trap* profile shows this. It asked for metal, but also for calm, quiet music (energy 0.20). The calm song "Spacewalk Thoughts" came first with 2.83 points. "Enter Sandman" is not in the top 5.

In my first formula (`classic`), genre was worth 2 points. "Enter Sandman" came first with 2.23 points, even though its energy is 0.97. That is why I changed the default.

### Why "Gym Hero" still shows up for Happy Pop fans

"Gym Hero" is a loud workout song. It is a strange pick for someone who wants happy pop. But its numbers look a lot like happy pop. It is upbeat (valence 0.77), and its energy (0.93) is close to the 0.80 target. It also carries the plain "pop" label.

| Song | Genre | Mood | Energy | Valence | Acousticness | Score |
|---|---|---|---|---|---|---|
| Sunrise City | pop (+1.0) | happy (+1.0) | +0.98 | +0.48 | +0.49 | **3.95** |
| Rooftop Lights | indie pop (no point) | happy (+1.0) | +0.96 | +0.49 | +0.43 | **2.88** |
| **Gym Hero** | **pop (+1.0)** | intense (no point) | +0.87 | +0.48 | +0.42 | **2.78** |

"Rooftop Lights" sounds the most like happy pop. It beats "Gym Hero" by only 0.10 points. "Rooftop Lights" gets its label point from its mood. "Gym Hero" gets its label point from the genre. The system sees "indie pop" and "pop" as two unrelated things, so "Rooftop Lights" gets nothing for its genre.

Only two songs have the plain "pop" label. Once "Sunrise City" is used up, "Gym Hero" is the only other song that can get the genre point. In `classic` mode, that point was worth 2, and "Gym Hero" ranked #2 above "Rooftop Lights". Now it ranks #3.

### The same middle songs show up everywhere

"Midnight Coding" is in the top 5 for 9 of the 12 profiles that run. "Love Yourz" is in 6 lists. "Let Me Love You" is in 5.

These songs have middle values for energy, valence, and acousticness. A middle song is never far from any target. So it collects decent points for almost any profile. In `classic` mode, "Midnight Coding" was in 7 lists. Scoring valence and acousticness gave middle songs more ways to score.

### Other patterns I found

- **Small genres get small lists.** A jazz fan (Dead Center) gets one strong match. "Coffee Shop Stories" scores 3.57. The other four songs are filler near 1.7 to 1.8. A lofi fan gets three real matches.
- **Scores bunch together.** The gap between #1 and #5 averages 1.63 across 8 test profiles. In `classic` mode it was 2.25. So near-ties are more common.
- **Filter bubble.** The top 5 for `low_energy` has three lofi songs, and two come from LoRoom. Every mode returns about 4 different genres in 5 songs. Changing the weights does not add variety.
- **Exact spelling needed.** "edm" does not match "EDM". "hip-hop", "rap", and "trap" count as three unrelated genres.
- **Energy gap is not fair to everyone.** A target of 0.0 can never score above 3.86. A target in the middle can get closer to 4.0. So scores are not comparable between people.
- **No "I don't know".** When nothing matches (*Wrong Case*, *Unknown Tastes*), the system still shows 5 songs. Nothing tells the user that no genre or mood matched.
- **Bad input is hidden, not caught.** In *Impossible Energy*, every energy line is negative, like "+-0.82". But the totals stay above zero, because valence and acousticness add points. An empty profile still crashes the program.
- **Energy and acousticness still move together.** In this catalog the correlation is -0.92. In *Calm Genre, Max Energy*, "Storm Runner" is loud but not acoustic, so it earns only +0.08 for acousticness. A listener who wants loud acoustic music is still not served.

---

## 6. Evaluation Process

I tested 13 profiles by running `python src/main.py`. I read the top 5 songs for each one. All of the output is in the README.

- **4 normal listeners:** `my_taste` (reflective hip-hop), `high_energy` (EDM, metal, trap), `low_energy` (classical, ambient, lofi), and `happy_pop` (pop, happy, energy 0.8).
- **9 trick listeners:** built to confuse the system.
  - *Sad Banger*: high energy but a sad mood.
  - *Calm Genre, Max Energy*: calm genres but maximum energy.
  - *Genre Trap*: metal, but quiet.
  - *Impossible Energy*: energy of -1.
  - *Wrong Case*: wrong capital letters.
  - *Unknown Tastes*: genres not in the catalog.
  - *Likes Everything*: every genre and mood.
  - *Empty Prefs*: no tastes at all.
  - *Dead Center*: energy 0.5 with one jazz match.

For normal listeners, I asked, "Would a person agree with these songs?" For trick listeners, I asked, "Does the system notice a problem, or does it quietly return something?"

I also ran two experiments, with my first formula (`classic`) as the baseline.

- **Experiment 1:** I cut the genre weight in half (2.0 to 1.0) and doubled the energy weight (1.0 to 2.0). The top 5 stayed the same for the three original normal listeners. *Genre Trap* finally put a calm song first. But now energy could beat genre and mood, so the bias just moved. The doubled energy weight also made the below-zero scores worse. I put the weights back.
- **Experiment 2:** I added valence and acousticness and built five ranking modes. I measured each one on 8 profiles. `balanced` fixed Genre Trap and the Gym Hero problem, so I made it the default. `genre_first` kept the genre problem. `mood_first` ignored energy requests. `energy_focused` washed out taste. The full tradeoffs are in the README.

### What surprised me

- **Likes Everything and Unknown Tastes still look the same.** They get the same 5 songs in the same order. Only the scores differ, by exactly 2.0. That is the genre point plus the mood point.
- **A listener with no matches gets almost the `my_taste` list.** *Unknown Tastes* shares 4 of its 5 songs with `my_taste`. Their number targets are close. When no label matches, the numbers decide.
- **Opposite energy, same top songs.** *Calm Genre, Max Energy* and `low_energy` both put "Spacewalk Thoughts" and "Clair de Lune" on top. One wants silence and one wants max energy. Genre and mood points (2 of 4) drown out the energy wish.
- **A valence target helps a little.** For *Sad Banger*, "Enter Sandman" (loud, valence 0.22) now makes the top 5. But "Levels" (valence 0.94) still wins, because genre, energy, and acousticness carry it.
- **The default hides a bug.** *Impossible Energy* has negative energy points, but the totals look normal.
- **Typos matter.** A lowercase "edm" hides every EDM song.
- **Empty is worse than everything.** "Likes Everything" works. "Empty Prefs" crashes.

### Profile pairs

**Normal listeners**

- **`high_energy` vs `low_energy`:** No songs in common. One list is loud and electric. The other is soft and acoustic. This is the clearest sign the system works.
- **`my_taste` vs `high_energy`:** Only "First Day Out" is shared. It is trap and very loud, so it fits both.
- **`my_taste` vs `low_energy`:** Only "Midnight Coding" is shared. It is gentle, and its numbers are close to what `my_taste` wants. It shows up for the numbers, not for taste.
- **`happy_pop` vs `high_energy`:** Two songs are shared, "Gym Hero" and "Sunrise City". For `high_energy` both are a good fit. They are loud and upbeat. For `happy_pop`, "Gym Hero" gets in on the pop label and the numbers.
- **`happy_pop` vs `low_energy`:** Nothing in common. That is what I expect for pop vs classical.

**Trick listeners**

- **Sad Banger vs `high_energy`:** Both want energy 0.95, and three songs are shared ("Levels", "First Day Out", "Enter Sandman"). Sad Banger adds sad moods, so two quiet sad songs take places 2 and 3. "Enter Sandman" is the closest thing to a sad banger, but it sits at #4. The system adds up wishes. It does not combine them.
- **Calm Genre, Max Energy vs `low_energy`:** 4 of 5 songs are shared, and the top two are the same. Only the loud filler differs. "Storm Runner" is #5 for Calm Genre, Max Energy.
- **Genre Trap vs `high_energy`:** "Enter Sandman" is #3 for `high_energy` and fits. It is not in the Genre Trap top 5, which is right for someone who wants calm music. Genre Trap's list shares 4 songs with the calm `low_energy` list.
- **Impossible Energy vs `happy_pop`:** Both are pop and happy, and both put "Sunrise City", "Rooftop Lights", and "Gym Hero" on top in that order. The only difference is the energy target. The impossible one still works, and only places 4 and 5 change.
- **Wrong Case vs `high_energy`:** Same taste, different capital letters. `high_energy` gets 3.92 for "Levels". Wrong Case gets nothing above 1.80.
- **Unknown Tastes vs `my_taste`:** Unknown Tastes has no matches. It shares 4 songs with `my_taste`, including "Love Yourz" at #1. So the numbers are the fallback.
- **Likes Everything vs Unknown Tastes:** Same 5 songs, same order. When everything matches, the labels stop meaning anything.
- **Likes Everything vs Empty Prefs:** Listing everything works. Listing nothing crashes. That is backwards for a brand new user.
- **Dead Center vs Unknown Tastes:** Both want energy 0.5. One jazz match moves "Coffee Shop Stories" to #1. Places 2 to 5 are the same four songs as places 1 to 4 for Unknown Tastes. One match moves one song, and the numbers do the rest.

---

## 7. Intended Use and Non-Intended Use

### Intended use

- Classroom learning. It shows how a content-based recommender turns data into a ranking.
- Practice with scoring rules, test profiles, and bias checks.
- Small demos where a person types in their tastes and gets 5 songs and the reasons why.

### Not intended for

- **Real music apps.** The catalog has 18 songs. That is far too small.
- **Judging anyone's taste.** A low score only means "does not match the labels".
- **Serious decisions.** For example, picking which artists get promoted.
- **Users outside the catalog.** If your music is not in these 15 genres, the results are just energy matches.
- **Learning from listening history.** It has none. It does not know who you are or what you skipped.

---

## 8. Ideas for Improvement

1. **Test the modes with real listeners.** I picked every weight by hand. Next I would ask people which top 5 they like best. Then I could choose the weights from real answers instead of my own guesses.
2. **Add variety and fix labels.** Limit the top 5 to 2 songs per genre or artist. Group related genres, like hip-hop, rap, and trap. Lowercase all text before matching. Give partial credit for close moods.
3. **Validate input and add songs.** Clamp energy points so they never go below 0. Reject empty profiles with a clear message. Add songs in the empty energy range (0.55 to 0.74) and for the genres with only one song.

---

## 9. Personal Reflection

### My biggest learning moment

My biggest learning moment was seeing how hard it is to build a scoring formula without too much bias. Every weight I picked favored someone. When I made genre worth less, energy took over. The bias did not go away. It just moved.

Building five ranking modes made this clearer. Each mode just picks which bias you accept. `balanced` fixed the Genre Trap and "Gym Hero" problems. But it also made the scores bunch together. A few middle-valued songs now show up everywhere. "Midnight Coding" is in 9 of the 12 lists that run. And no mode added variety.

I also learned that real recommenders probably need a lot of data to find the best formula. I picked every weight by hand, using 18 songs. To do better, I would need real listeners to tell me which top 5 they like.

### How AI tools helped me, and when I double-checked them

AI helped most when I wanted to test something. It helped me build the trick profiles and run them quickly. It helped me write tests. It also helped me work out the scoring formula and try the ranking modes.

I still had to check its work, because some of it was wrong:

- One test it wrote used a song that matched genre and mood. So the test did not catch the negative-score bug it was meant to catch. Running the tests showed it.
- The run command in the README did not work. I only found out by running it.
- Some comparisons in this model card were worded too loosely. For example, one said two lists were "the same" when only two songs overlapped.
- A new default mode could only reach 3.5 out of 4.0 for one kind of profile. A check on the score math found it.

The AI could write the code and the explanations fast. But I had to be the one to run everything and confirm the claims matched what the program printed.

### What surprised me about simple algorithms

I was surprised by how much a simple formula can feel like it "knows" me. I only typed in a few inputs. Depending on the profile, the top 5 songs still felt like songs I would really listen to.

Then the trick profiles showed the other side. A listener who likes everything and a listener who matches nothing got the same five songs in the same order. The system was only adding up points. It never understood the music.

### What I would try next

I would add more songs first. The catalog has gaps in energy, and 13 of the 15 genres have only one song. Then I would fine-tune the formula so there is less bias. I would start with the fixes in the Ideas for Improvement section:

- Test the modes with real listeners.
- Limit how many songs from one genre or artist show up.
- Catch bad input, like empty profiles and impossible energy targets.
