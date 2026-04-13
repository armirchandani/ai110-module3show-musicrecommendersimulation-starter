import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Challenge 2 — Weight presets for multiple scoring modes
# ---------------------------------------------------------------------------
DEFAULT_WEIGHTS = {"genre": 2.0, "mood": 1.0, "energy": 1.0, "acoustic": 0.5}
GENRE_FIRST     = {"genre": 3.0, "mood": 0.5, "energy": 0.5, "acoustic": 0.25}
MOOD_FIRST      = {"genre": 1.0, "mood": 3.0, "energy": 0.5, "acoustic": 0.25}
ENERGY_FOCUSED  = {"genre": 0.5, "mood": 0.5, "energy": 3.0, "acoustic": 0.25}

# ---------------------------------------------------------------------------
# Data classes (required by tests/test_recommender.py)
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """Represents a song and its attributes. Required by tests/test_recommender.py"""
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
    """Represents a user's taste preferences. Required by tests/test_recommender.py"""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """OOP implementation of the recommendation logic. Required by tests/test_recommender.py"""

    def __init__(self, songs: List[Song]):
        """Store the catalog of Song dataclass instances for later scoring."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects for the given UserProfile. Not yet implemented."""
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-English explanation of why song was recommended to user. Not yet implemented."""
        # TODO: Implement explanation logic
        return "Explanation placeholder"

# ---------------------------------------------------------------------------
# Functional API
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """
    Load songs from a CSV file and return them as a list of typed dicts.

    Type conversions applied per row:
      id, popularity, release_decade  → int
      energy, tempo_bpm, valence,
      danceability, acousticness      → float
      mood_tag, title, artist, etc.   → str (unchanged)
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"]             = int(row["id"])
            row["energy"]         = float(row["energy"])
            row["tempo_bpm"]      = float(row["tempo_bpm"])
            row["valence"]        = float(row["valence"])
            row["danceability"]   = float(row["danceability"])
            row["acousticness"]   = float(row["acousticness"])
            row["popularity"]     = int(row["popularity"])
            row["release_decade"] = int(row["release_decade"])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict, weights: Dict = None) -> Tuple[float, List[str]]:
    """
    Score a single song against user preferences using configurable weights.

    Core rules (weight-controlled via the weights dict):
      genre match    — weights["genre"]   if genres match (case-insensitive)
      mood match     — weights["mood"]    if moods match (case-insensitive)
      energy prox.   — weights["energy"] * (1 - |song_energy - target_energy|)
      acoustic bonus — weights["acoustic"] if likes_acoustic and acousticness > 0.5

    Extended rules (Challenge 1, fixed weights):
      mood tag match  — +0.50 if song mood_tag == user favorite_mood_tag
      popularity boost— +0.30 * (popularity / 100), always contributes a small amount
      decade match    — +0.75 if song release_decade == user preferred_decade

    Returns (total_score, list_of_reason_strings).
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    score = 0.0
    reasons = []

    # Core rule 1 — genre match
    if song["genre"].lower() == user_prefs["favorite_genre"].lower():
        pts = weights["genre"]
        score += pts
        reasons.append(f"genre match (+{pts:.2f})")

    # Core rule 2 — mood match
    if song["mood"].lower() == user_prefs["favorite_mood"].lower():
        pts = weights["mood"]
        score += pts
        reasons.append(f"mood match (+{pts:.2f})")

    # Core rule 3 — energy proximity
    energy_pts = weights["energy"] * (1 - abs(song["energy"] - user_prefs["target_energy"]))
    score += energy_pts
    reasons.append(f"energy match (+{energy_pts:.2f})")

    # Core rule 4 — acoustic bonus
    if user_prefs.get("likes_acoustic") and song["acousticness"] > 0.5:
        pts = weights["acoustic"]
        score += pts
        reasons.append(f"acoustic match (+{pts:.2f})")

    # Extended rule 1 — mood tag match
    if user_prefs.get("favorite_mood_tag") and song.get("mood_tag") == user_prefs["favorite_mood_tag"]:
        score += 0.5
        reasons.append("mood tag match (+0.50)")

    # Extended rule 2 — popularity boost (always fires)
    pop_boost = 0.3 * (song["popularity"] / 100)
    score += pop_boost
    reasons.append(f"popularity boost (+{pop_boost:.2f})")

    # Extended rule 3 — decade match
    if user_prefs.get("preferred_decade") and song.get("release_decade") == user_prefs["preferred_decade"]:
        score += 0.75
        reasons.append("decade match (+0.75)")

    return (score, reasons)


def score_song_experimental(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Legacy experimental scorer from Phase 3: genre weight halved to +1.0, energy doubled to ×2.0.
    Superseded by the weights parameter on score_song() but kept for historical comparison.
    """
    return score_song(
        user_prefs, song,
        weights={"genre": 1.0, "mood": 1.0, "energy": 2.0, "acoustic": 0.5},
    )


def diversify_results(
    scored_songs: List[Tuple[Dict, float, str]], top_k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Re-rank a pre-sorted scored list to enforce genre and artist diversity.

    Iterates through scored_songs in score order (highest first) and adds a song
    to the output only when both conditions hold:
      - The song's genre has appeared fewer than 2 times in the output so far
      - The song's artist has not yet appeared in the output

    Stops once top_k songs are selected or the full catalog is exhausted.
    The output may be shorter than top_k if the catalog is too small to satisfy
    the diversity constraints.
    """
    result: List[Tuple[Dict, float, str]] = []
    genre_counts: Dict[str, int] = {}
    seen_artists: set = set()

    for song, score, explanation in scored_songs:
        genre  = song["genre"]
        artist = song["artist"]

        if genre_counts.get(genre, 0) >= 2:
            continue
        if artist in seen_artists:
            continue

        result.append((song, score, explanation))
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
        seen_artists.add(artist)

        if len(result) >= top_k:
            break

    return result


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    scorer=None,
    weights: Dict = None,
    diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """
    Score and rank all songs against user_prefs, returning the top k.

    Parameters
    ----------
    scorer    : optional callable (user_prefs, song) -> (score, reasons).
                When provided, the weights param is ignored.
    weights   : passed to score_song() to control rule weights.
                Ignored when scorer is provided. Uses DEFAULT_WEIGHTS if None.
    diversity : when True, passes the full ranked list through diversify_results()
                before slicing to k, enforcing genre and artist variety.

    Returns a list of (song_dict, score, explanation_string) tuples, sorted
    descending by score.  If k exceeds the catalog size, all songs are returned.
    """
    if scorer is None:
        scorer = lambda u, s: score_song(u, s, weights=weights)

    scored = []
    for song in songs:
        score, reasons = scorer(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))

    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    if diversity:
        return diversify_results(ranked, top_k=k)
    return ranked[:k]
