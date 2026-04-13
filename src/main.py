"""
Command line runner for the Music Recommender Simulation.

Runs all 5 user profiles plus two experiments:
  Challenge 2 — three scoring-mode presets compared for Happy Pop Fan
  Challenge 3 — diversity filter on vs. off for Happy Pop Fan
All output uses the format_results_table() formatter (Challenge 4).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from recommender import (
    load_songs,
    recommend_songs,
    GENRE_FIRST,
    MOOD_FIRST,
    ENERGY_FOCUSED,
)

# ---------------------------------------------------------------------------
# User profiles (Challenge 1 — new fields: favorite_mood_tag, preferred_decade)
# ---------------------------------------------------------------------------
PROFILES = [
    ("Happy Pop Fan", {
        "favorite_genre":   "pop",
        "favorite_mood":    "happy",
        "target_energy":    0.8,
        "likes_acoustic":   False,
        "favorite_mood_tag": "uplifting",
        "preferred_decade": 2020,
    }),
    ("Chill Lofi", {
        "favorite_genre":   "lofi",
        "favorite_mood":    "chill",
        "target_energy":    0.3,
        "likes_acoustic":   True,
        "favorite_mood_tag": "dreamy",
        "preferred_decade": 2020,
    }),
    ("Intense Rock", {
        "favorite_genre":   "metal",
        "favorite_mood":    "intense",
        "target_energy":    0.9,
        "likes_acoustic":   False,
        "favorite_mood_tag": "aggressive",
        "preferred_decade": 2010,
    }),
    ("Conflicted Listener", {
        "favorite_genre":   "jazz",
        "favorite_mood":    "happy",
        "target_energy":    0.9,
        "likes_acoustic":   True,
        "favorite_mood_tag": "nostalgic",
        "preferred_decade": 2000,
    }),
    ("Genre Ghost", {
        "favorite_genre":   "country",
        "favorite_mood":    "focused",
        "target_energy":    0.5,
        "likes_acoustic":   False,
        "favorite_mood_tag": "gritty",
        "preferred_decade": 1990,
    }),
]

HAPPY_POP_PREFS = {
    "favorite_genre":   "pop",
    "favorite_mood":    "happy",
    "target_energy":    0.8,
    "likes_acoustic":   False,
    "favorite_mood_tag": "uplifting",
    "preferred_decade": 2020,
}

# ---------------------------------------------------------------------------
# Challenge 4 — Visual summary table
# ---------------------------------------------------------------------------
_TITLE_W   = 22
_ARTIST_W  = 18
_SCORE_W   =  7
_REASONS_W = 42
_SEP_W     = 2 + 5 + 1 + _TITLE_W + 1 + _ARTIST_W + 1 + _SCORE_W + 1 + _REASONS_W
_SEP       = "─" * _SEP_W


def format_results_table(profile_name: str, results: list, total_songs: int) -> None:
    """
    Print a fixed-width ASCII table for a recommendation result set.

    Columns: Rank (5) | Title (22) | Artist (18) | Score (7) | Reasons (42)
    Title and Reasons are truncated to fit. Footer shows total songs scored
    and the highest score in the result set.
    """
    top_score = results[0][1] if results else 0.0
    print(f"\n{_SEP}")
    print(f"  {profile_name}")
    print(_SEP)
    print(
        f"  {'Rank':<5} {'Title':<{_TITLE_W}} {'Artist':<{_ARTIST_W}}"
        f" {'Score':>{_SCORE_W}} Reasons"
    )
    print(
        f"  {'----':<5} {'-' * _TITLE_W:<{_TITLE_W}} {'-' * _ARTIST_W:<{_ARTIST_W}}"
        f" {'-------':>{_SCORE_W}} {'-' * _REASONS_W}"
    )
    for i, (song, score, explanation) in enumerate(results, start=1):
        title   = song["title"][:_TITLE_W]
        artist  = song["artist"][:_ARTIST_W]
        reasons = explanation[:_REASONS_W]
        print(
            f"  {i:<5} {title:<{_TITLE_W}} {artist:<{_ARTIST_W}}"
            f" {score:>{_SCORE_W}.2f} {reasons}"
        )
    print(_SEP)
    print(f"  Songs scored: {total_songs}   Top score: {top_score:.2f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # --- All 5 profiles ---
    print("\n" + "=" * _SEP_W)
    print("  ALL PROFILES")
    print("=" * _SEP_W)
    for profile_name, user_prefs in PROFILES:
        recs = recommend_songs(user_prefs, songs, k=5)
        format_results_table(profile_name, recs, len(songs))

    # --- Challenge 2: three scoring modes ---
    print("\n" + "=" * _SEP_W)
    print("  CHALLENGE 2 — Scoring Mode Comparison: Happy Pop Fan")
    print("=" * _SEP_W)
    modes = [
        ("Genre First  (genre×3, mood×0.5, energy×0.5)", GENRE_FIRST),
        ("Mood First   (genre×1, mood×3,   energy×0.5)", MOOD_FIRST),
        ("Energy Focus (genre×0.5, mood×0.5, energy×3)", ENERGY_FOCUSED),
    ]
    for mode_name, w in modes:
        recs = recommend_songs(HAPPY_POP_PREFS, songs, k=5, weights=w)
        format_results_table(f"Happy Pop Fan — {mode_name}", recs, len(songs))

    # --- Challenge 3: diversity filter ---
    print("\n" + "=" * _SEP_W)
    print("  CHALLENGE 3 — Diversity Comparison: Happy Pop Fan")
    print("=" * _SEP_W)
    recs_std = recommend_songs(HAPPY_POP_PREFS, songs, k=5, diversity=False)
    recs_div = recommend_songs(HAPPY_POP_PREFS, songs, k=5, diversity=True)
    format_results_table("Happy Pop Fan — No Diversity Filter",   recs_std, len(songs))
    format_results_table("Happy Pop Fan — With Diversity Filter", recs_div, len(songs))


if __name__ == "__main__":
    main()
