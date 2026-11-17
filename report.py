"""
report.py - PROTOTYPE. Writes report.md: a one-page engagement report built
from the latest pull, and what changed since the previous pull (if any).

Run after fetch_data.py:  py report.py

It makes no API calls. It reads the snapshots/ folders that fetch_data.py writes,
so "previous pull" means the second-newest folder in snapshots/.
"""

import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")


def load_snapshots():
    runs = sorted(p for p in Path("snapshots").iterdir() if (p / "islands_clean.csv").exists())
    if not runs:
        sys.exit("No snapshots found. Run fetch_data.py first.")
    current = pd.read_csv(runs[-1] / "islands_clean.csv", encoding="utf-8-sig")
    previous = pd.read_csv(runs[-2] / "islands_clean.csv", encoding="utf-8-sig") if len(runs) > 1 else None
    return runs, current, previous


def md_table(df):
    """Small markdown table writer (avoids needing the 'tabulate' package)."""
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in r.values) + " |")
    return "\n".join(lines)


def fmt_int(x):
    return "" if pd.isna(x) else f"{int(x):,}"


def main():
    runs, cur, prev = load_snapshots()
    out = []
    p = out.append
    p("# Fortnite island engagement report (PROTOTYPE)")
    p("")
    p(f"- Pull: `{cur['pulled_at'].iloc[0]}` (snapshot `{runs[-1].name}`)")
    p(f"- Metrics day: **{cur['metrics_date'].iloc[0]} (UTC)**. Every '24h' number covers that one day.")
    p(f"- Islands in the clean dataset: **{len(cur)}** (a sample, not all of Fortnite; see README for how they were chosen).")
    p("")

    # 1. Top 10 by peak CCU
    p("## 1. Top 10 islands by peak concurrent players")
    top = cur.nlargest(10, "peak_ccu_24h").reset_index(drop=True)
    t = pd.DataFrame({
        "#": range(1, len(top) + 1),
        "Island": top["title"],
        "Epic-made": top["epic_made"],
        "Genre": top["genre"].fillna("(not ranked)"),
        "Peak CCU": top["peak_ccu_24h"].map(fmt_int),
        "Unique players": top["unique_players_24h"].map(fmt_int),
        "D1 retention": top["retention_d1"].map("{:.0%}".format),
        "Avg min/player": top["avg_minutes_per_player"].round(1),
    })
    p(md_table(t))
    p("")

    # 2. Retention summary
    p("## 2. Retention summary (share of players who came back)")
    ret = cur[["retention_d1", "retention_d7"]].describe(percentiles=[0.25, 0.5, 0.75]).T
    ret = ret[["count", "mean", "min", "25%", "50%", "75%", "max"]].round(3).reset_index()
    ret = ret.rename(columns={"index": "metric", "50%": "median"})
    ret["count"] = ret["count"].astype(int)
    p(md_table(ret))
    p("")
    p("Epic's spec defines D1 as players 'retained from the previous day' and D7 as players 'retained from "
      "the previous 7 days'. The API returns both as 0-1 fractions rounded to 2 decimals (the spec calls "
      "them a 'number of players'), so read 0.17 as 17%.")
    p("")

    # 3. Epic-made vs creator-made
    p("## 3. Epic-made vs creator-made islands")
    grp = cur.groupby("epic_made").agg(
        islands=("island_code", "count"),
        median_peak_ccu=("peak_ccu_24h", "median"),
        median_d1=("retention_d1", "median"),
        median_d7=("retention_d7", "median"),
        median_avg_minutes=("avg_minutes_per_player", "median"),
        median_plays_per_player=("plays_per_player", "median"),
    ).round(3).reset_index()
    p(md_table(grp))
    p("")
    n_epic = int((cur["epic_made"] == "Yes").sum())
    p(f"**Caution:** only {n_epic} Epic-made island(s) are in the sample, and creator islands were picked "
      "from several ranks per genre (including small islands). Medians here describe this sample only; "
      "they are not a fair Epic-vs-creator benchmark.")
    p("")

    # 4. Change vs previous pull
    p("## 4. Changes since the previous pull")
    if prev is None:
        p("No previous pull yet. Run fetch_data.py again on a later day and re-run report.py to see changes.")
    else:
        p(f"Previous pull: `{prev['pulled_at'].iloc[0]}` (metrics day {prev['metrics_date'].iloc[0]}).")
        if prev["metrics_date"].iloc[0] == cur["metrics_date"].iloc[0]:
            p("")
            p("Both pulls cover the **same metrics day**, so any difference below is a data revision "
              "or a different island sample, not a change in player behaviour.")
        m = cur.merge(prev, on="island_code", how="outer", suffixes=("", "_prev"), indicator=True)
        new = m[m["_merge"] == "left_only"]
        gone = m[m["_merge"] == "right_only"]
        both = m[m["_merge"] == "both"].copy()
        both["peak_ccu_change_pct"] = ((both["peak_ccu_24h"] / both["peak_ccu_24h_prev"] - 1) * 100).round(1)
        both["d1_change_pts"] = ((both["retention_d1"] - both["retention_d1_prev"]) * 100).round(1)
        p("")
        p(f"- Islands in both pulls: {len(both)}; new this pull: {len(new)}; no longer in clean set: {len(gone)}")
        if len(new):
            p(f"- New: {', '.join(new['title'].astype(str).head(15))}")
        if len(gone):
            p(f"- Dropped: {', '.join(gone['title_prev'].astype(str).head(15))}")
        movers = both.reindex(both["peak_ccu_change_pct"].abs().sort_values(ascending=False).index).head(10)
        p("")
        p("Biggest peak-CCU moves among islands in both pulls:")
        p("")
        p(md_table(pd.DataFrame({
            "Island": movers["title"],
            "Peak CCU before": movers["peak_ccu_24h_prev"].map(fmt_int),
            "Peak CCU now": movers["peak_ccu_24h"].map(fmt_int),
            "Change %": movers["peak_ccu_change_pct"],
            "D1 change (pts)": movers["d1_change_pts"],
        })))
    p("")
    p("---")
    p("_Prototype: numbers come straight from islands_clean.csv. No forecasting, no causal claims._")

    Path("report.md").write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote report.md ({len(cur)} islands, previous pull: {'yes' if prev is not None else 'none'})")


if __name__ == "__main__":
    main()
