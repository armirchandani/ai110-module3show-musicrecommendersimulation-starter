# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 is a content-based music recommender built for classroom exploration. Given a user's stated preferences for genre, mood, energy level, and whether they enjoy acoustic sound, it returns the five songs from an 18-song catalog that best match those preferences.

**This system is appropriate for:**
- Learning how recommender systems turn raw data into ranked lists
- Prototyping and explaining the logic behind content-based filtering
- Classroom demonstrations of algorithm design trade-offs

**This system should NOT be used for:**
- A real music product serving diverse or real-world users
- Any context where personalization should be based on actual listening history or behavior
- Replacing genuine taste data with user-supplied labels in a production setting

---

## 3. How the Model Works

Every song in the catalog has a set of numerical and categorical attributes: genre, mood, energy, tempo, valence, danceability, and acousticness. When a user provides their preferences, the system computes a score for each song by applying four rules and adding up the points:

1. **Genre match (+2.0 points):** If the song's genre matches the user's favorite genre exactly, it earns the highest reward. This is the most influential single signal in the formula.
2. **Mood match (+1.0 point):** If the song's mood label matches the user's preferred mood, it earns one additional point.
3. **Energy proximity (up to +1.0 point):** The system measures how close the song's energy level is to the user's target on a 0–1 scale. A perfect match earns the full point; a song at the opposite end of the energy spectrum earns close to nothing.
4. **Acoustic bonus (+0.5 points):** If the user has said they like acoustic music and the song has an acousticness value above 0.5, it earns a small bonus.

After every song is scored, the list is sorted from highest to lowest, and the top five are returned with a plain-English explanation of which rules fired and how many points each contributed.

---

## 4. Data

The catalog contains **18 songs**, each described by 10 features:

| Feature | What it means |
|---|---|
| id | Unique number for each song |
| title | Song name |
| artist | Artist name |
| genre | Musical genre (pop, lofi, rock, jazz, metal, classical, etc.) |
| mood | Emotional tag (happy, chill, intense, relaxed, moody, focused, etc.) |
| energy | How energetic the song feels, from 0.0 (very calm) to 1.0 (very intense) |
| tempo_bpm | Speed of the song in beats per minute |
| valence | How musically positive or upbeat the song sounds (0.0–1.0) |
| danceability | How suitable the song is for dancing (0.0–1.0) |
| acousticness | How acoustic versus electronic the song sounds (0.0–1.0) |

The original starter dataset had 10 songs, mostly pop and lofi. Eight songs were added to cover underrepresented styles: jazz, ambient, metal, classical, hip-hop, blues, electronic, and folk.

**What is missing from this dataset:**
- No play counts, stream counts, or popularity data
- No user history — the system has never observed what anyone actually listened to
- No lyrics, language, or lyric themes
- No artist similarity data (e.g., "fans of Artist X also listen to Artist Y")
- No time-of-day or situational context signals (commuting, studying, working out)
- The "country" genre has zero songs, so country-preferring users get no genre-matched results at all

---

## 5. Strengths

The system works best when a user's genre preference is well-represented in the catalog. Profiles like "Chill Lofi" and "Intense Rock" produce intuitive, coherent top-5 lists because the catalog has multiple songs in those genres that vary meaningfully in mood and energy. The energy proximity rule does a reasonable job of differentiating songs within a genre — a lofi user who wants energy 0.3 correctly ranks Library Rain above Focus Flow because Library Rain's energy (0.35) is closer to the target. The explanation output also makes the system transparent: every recommendation comes with a specific reason, which helps a user understand why they are seeing each song rather than experiencing the recommendation as an unexplained black box.

---

## 6. Limitations and Bias

When a user's favorite genre does not appear anywhere in the catalog — such as "country" — the genre match term contributes zero points for every song, and the system silently falls back to ranking entirely by energy proximity and mood. The user receives recommendations with no warning that their core preference was ignored, which in a real product would feel broken or confusing.

The genre weight (+2.0) is the single largest term in the scoring formula, nearly double the mood weight (+1.0) and twice the maximum possible energy score (+1.0). This means a genre match almost always overrides strong signals in other dimensions: a jazz song that perfectly matches a user's energy and mood target will still score lower than a pop song with a poor energy match, simply because the genre label matched. The "Conflicted Listener" test case showed this directly — both jazz songs topped the list despite having energy around 0.4 against a target of 0.9, and neither matched the user's happy mood preference.

Because the catalog contains only 18 songs and genres are not evenly distributed (lofi has 3 songs, pop has 2, metal has 1, country has 0), users whose preferred genre has more songs in the catalog get more meaningful competition among high-scoring matches. Users whose genre appears only once or not at all are effectively penalized by dataset gaps rather than by anything meaningful about their taste.

The energy proximity formula — `1 - abs(song_energy - target_energy)` — is linear, which means it treats a 0.1 difference and a 0.9 difference as simply scaled versions of the same problem. A squared or exponential penalty would push songs far from the target much lower in the rankings, but the current formula keeps them deceptively competitive.

Finally, the acoustic bonus (+0.5) only activates when `likes_acoustic` is True, creating an asymmetry: users who prefer acoustic music get an extra scoring dimension, while users who do not are limited to three signals. This subtly advantages acoustic-preferring users in a catalog that happens to have many high-acousticness songs.

---

## 7. Evaluation

Five user profiles were tested to probe different parts of the scoring logic:

- **Happy Pop Fan** — well-matched to the catalog; top result (Sunrise City) scored 3.98 with genre, mood, and energy all firing. Results felt intuitively correct.
- **Chill Lofi** — also well-served; the acoustic bonus activated for multiple songs and helped meaningfully separate closely-scored results. Library Rain edged Midnight Coding because its energy (0.35) was closer to the target of 0.3.
- **Intense Rock** — only one metal song exists in the catalog, so it dominated at #1 with a score of 3.93. The rest of the top 5 was filled by mood-matching songs from other genres, which felt reasonable given the constraint.
- **Conflicted Listener** (jazz + happy mood + high energy + likes acoustic) — exposed a tension in the data: both jazz songs in the catalog are low-energy and not tagged happy, yet the genre weight pulled them to #1 and #2 despite poor fits on every other dimension. This confirmed that +2.0 for genre is sometimes too strong.
- **Genre Ghost** (country + focused mood + 0.5 energy) — country does not exist in the dataset. The genre term was zero for every song. The system silently fell back to mood and energy only, producing a genre-incoherent top 5 with no transparency about the fallback.

A weight experiment was also run on the Happy Pop Fan profile comparing standard weights (genre +2.0, energy ×1.0) against energy-heavy weights (genre +1.0, energy ×2.0). The only rank change was Gym Hero dropping from #2 to #3 and Rooftop Lights rising from #3 to #2. Under standard weights, Gym Hero's genre match propped it above Rooftop Lights despite a worse energy fit. Once the energy multiplier doubled, Rooftop Lights' closer energy (0.76 vs. target 0.8) outweighed the genre bonus — exactly the tradeoff the experiment was designed to surface.

---

## 8. Future Work

Three concrete improvements would have the most impact:

1. **Add collaborative filtering using play count or skip data.** Right now the system only knows what a user says they want. A real recommender would also look at what similar users actually listened to, skipped, or replayed — behavioral signals that reveal taste in ways explicit preferences cannot capture.

2. **Replace linear energy scoring with a curve that penalizes large gaps more heavily.** The current formula scores a song 0.3 away from the target as only slightly worse than one 0.05 away. A squared penalty — `1 - (distance²)` — would push far-off songs much lower in the rankings and create a more natural "close match wins" behavior.

3. **Expand the dataset to 100+ songs so no genre is over-represented.** With 18 songs, lofi has 3 slots and country has 0. A larger and more balanced catalog would make genre weights meaningful across all user types rather than only those whose preferred genre happens to be well-stocked.

---

## 9. Personal Reflection

Building VibeFinder 1.0 made the mechanics of recommender systems feel concrete in a way that reading about them does not. Assigning explicit numbers to things like "how much should genre matter compared to energy?" forced a real design decision rather than an abstract one — and running adversarial profiles like Genre Ghost immediately revealed where those decisions break down in ways that are hard to predict in advance. The most striking moment was the Conflicted Listener results: the system confidently surfaced two jazz songs despite them being almost entirely wrong for the user's energy and mood, purely because the genre label matched. That felt like a miniature version of how real recommendation engines can be confidently wrong while still appearing to give a reasoned answer.
