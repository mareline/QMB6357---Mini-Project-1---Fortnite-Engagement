"""
build_context.py - PROTOTYPE. Writes fortnite_context.md: an LLM-ready context
file (metric definitions, how each field was collected, known limits, the data
itself, and 10 test questions with answers computed from the real data).

Run after fetch_data.py:  py build_context.py

Use: paste fortnite_context.md (minus the "Answer key" section) into an LLM,
ask the 10 questions, and compare its replies with the answer key. Questions 9
and 10 are traps: the correct answer is "the data does not say".
"""

import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")


def main():
    c = pd.read_csv("islands_clean.csv", encoding="utf-8-sig")
    a = pd.read_csv("islands_all.csv", encoding="utf-8-sig")
    x = pd.read_csv("excluded.csv", encoding="utf-8-sig")
    h = pd.read_csv("daily_history.csv", encoding="utf-8-sig")
    day = c["metrics_date"].iloc[0]
    pulled = c["pulled_at"].iloc[0]

    # ---------------- answers computed from the data ----------------
    top = c.loc[c["peak_ccu_24h"].idxmax()]
    creators = c[c["epic_made"] == "No"]
    best_creator_d1 = creators.loc[creators["retention_d1"].idxmax()]
    group_counts = c["genre_group"].value_counts()
    p33, p67 = c["peak_ccu_24h"].quantile([1 / 3, 2 / 3])
    br_code = c.loc[c["peak_ccu_24h"].idxmax(), "island_code"]
    br_hist = h[h["island_code"] == br_code]
    br_peak_day = br_hist.loc[br_hist["peak_ccu"].idxmax()]
    reload = c[c["title"] == "Reload"]
    null_d7 = x[x["reason"].str.contains("retention_d7: null", na=False)
                & ~x["reason"].str.contains("peak_ccu_24h", na=False)]
    trap = null_d7.iloc[0] if len(null_d7) else None
    median_d1 = c["retention_d1"].median()

    qa = [
        (f"Which island had the highest peak concurrent players on {day} (UTC), and what was the value?",
         f"{top['title']} ({top['island_code']}) with {int(top['peak_ccu_24h']):,}."),
        ("How many islands are in the clean dataset, and how many pulled islands were excluded?",
         f"{len(c)} clean; {len(x)} excluded (of {len(a)} pulled)."),
        ("What is the median D1 retention across the clean islands? Give it as a percentage.",
         f"{median_d1:.1%} (retention_d1 median = {median_d1:.3f})."),
        ("Which genre_group has the most islands in the clean dataset, and how many?",
         f"{group_counts.index[0]} with {group_counts.iloc[0]} islands."),
        ("What was Reload's average minutes per player on the metrics day?",
         f"{reload['avg_minutes_per_player'].iloc[0]} minutes." if len(reload) else "Reload is not in the clean data."),
        ("Among creator-made (not Epic) islands, which had the highest D1 retention?",
         f"{best_creator_d1['title']} ({best_creator_d1['island_code']}) at {best_creator_d1['retention_d1']:.2f}."),
        ("What peak_ccu_24h values separate the Low, Medium and High ccu_tier groups?",
         f"Low <= {p33:,.1f}; Medium > {p33:,.1f} and <= {p67:,.1f}; High > {p67:,.1f}."),
        (f"On which day in the 7-day history did {top['title']} have its highest peak CCU, and what was it?",
         f"{br_peak_day['date']} with {int(br_peak_day['peak_ccu']):,}."),
        (f"What was the D7 retention of {trap['title']} ({trap['island_code']})?" if trap is not None
         else "What was the D7 retention of an excluded island?",
         "Not available: the API returned null for retention_d7 on that day (Epic returns null when "
         "there is too little data, e.g. fewer than 5 unique players). It must not be guessed or treated as 0."),
        (f"How many days ago was {top['title']} released?",
         "The data cannot answer this: the Fortnite Data API does not provide a release date."),
    ]

    # ---------------- the context file ----------------
    cols = ["island_code", "title", "creator", "epic_made", "genre", "genre_group",
            "peak_ccu_24h", "plays_24h", "unique_players_24h", "avg_minutes_per_player",
            "favorites", "recommendations", "retention_d1", "retention_d7", "ccu_tier", "retention_tier"]
    out = []
    p = out.append
    p("# Fortnite island engagement: context file for LLM questions (PROTOTYPE)")
    p("")
    p("You are answering questions about a small sample of Fortnite islands. Use ONLY the data and "
      "definitions in this file. If the file does not contain the answer, say so. Never estimate a "
      "missing value.")
    p("")
    p("## Source and timing")
    p(f"- Source: Epic Games' public Fortnite Data API, `https://api.fortnite.com/ecosystem/v1` (spec v1.1.0).")
    p(f"- Pulled at: {pulled}. All '24h' metrics are for the full UTC day **{day}**.")
    p(f"- Sample: {len(a)} islands pulled, {len(c)} with complete data (the table below). The sample is "
      "5 islands from each of Epic's 13 discovery genres (ranks 1, 10, 50, 150 and 400 in an hourly genre "
      "ranking) plus 2 Epic-made modes (Battle Royale, Reload). It is NOT all of Fortnite and NOT a random sample.")
    p("")
    p("## Metric definitions (Epic's wording, plus what the data actually looks like)")
    p("| Column | Definition | Unit / format | Endpoint |")
    p("|---|---|---|---|")
    defs = [
        ("peak_ccu_24h", "Peak number of concurrent players playing the island", "players", "peakCCU"),
        ("plays_24h", "Times players started the island; repeat starts by the same player each count", "plays", "plays"),
        ("unique_players_24h", "Number of unique players playing the island", "players", "uniquePlayers"),
        ("minutes_played_24h", "Total minutes players spent on the island", "minutes", "minutesPlayed"),
        ("avg_minutes_per_player", "Average minutes per player", "minutes", "averageMinutesPerPlayer"),
        ("favorites", "Times the island was added to a player's favorites", "count", "favorites"),
        ("recommendations", "Times the island was recommended by a player", "count", "recommendations"),
        ("retention_d1", "Spec: 'players retained from the previous day'", "0-1 fraction, 2 decimals", "retention (d1)"),
        ("retention_d7", "Spec: 'players retained from the previous 7 days'", "0-1 fraction, 2 decimals", "retention (d7)"),
        ("plays_per_player", "plays_24h / unique_players_24h (derived)", "ratio", "-"),
        ("favorite_rate", "favorites / unique_players_24h (derived)", "ratio", "-"),
        ("recommend_rate", "recommendations / unique_players_24h (derived)", "ratio", "-"),
        ("ccu_tier", "Low/Medium/High terciles of peak_ccu_24h within this sample", "text", "-"),
        ("retention_tier", "Low/Medium/High terciles of retention_d1 within this sample", "text", "-"),
        ("genre / genre_group", "Epic discovery genre of the ranking the island came from / 4 broader groups", "text", "/genres/{slug}/rankings"),
        ("epic_made", "Yes if the island's creatorCode is 'epic'", "Yes/No", "/islands/{code}"),
    ]
    for d in defs:
        p("| " + " | ".join(d) + " |")
    p("")
    p("Metric columns come from `GET /islands/{code}/metrics/day` (one daily bucket per UTC day). Island "
      "title, creator, tags and createdIn come from `GET /islands/{code}`.")
    p("")
    p("## Known limits")
    p("- Only 7 days of history exist in the API; this is a snapshot, not a long-term trend.")
    p("- Epic returns **null** when an island had fewer than 5 unique players in the interval. Nulls are "
      "excluded from the clean table, never replaced by 0.")
    p("- Only public, discoverable islands are in the API.")
    p("- Favorites and recommendations can be 0 for some Epic-made modes because Epic does not track them there.")
    p("- Retention is a 0-1 fraction rounded to 2 decimals, although Epic's spec calls it a 'number of players'.")
    p("- The API has no release date, so island age cannot be computed.")
    p("- Only 2 Epic-made islands are in the sample; Epic vs creator comparisons are not representative.")
    p("")
    p(f"## Data: clean islands ({len(c)} rows, metrics day {day})")
    p("```csv")
    p(c[cols].to_csv(index=False).strip())
    p("```")
    p("")
    p("## Data: excluded islands and why")
    p("```csv")
    p(x.to_csv(index=False).strip())
    p("```")
    p("")
    p("## Data: daily history (7 UTC days) for the 10 largest islands by peak CCU")
    p("```csv")
    p(h.to_csv(index=False).strip())
    p("```")
    p("")
    p("## Test questions")
    for i, (q, _) in enumerate(qa, 1):
        p(f"{i}. {q}")
    p("")
    p("## Answer key (remove this section before giving the file to the LLM)")
    for i, (_, ans) in enumerate(qa, 1):
        p(f"{i}. {ans}")
    Path("fortnite_context.md").write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote fortnite_context.md with {len(qa)} test questions")


if __name__ == "__main__":
    main()
