"""
fetch_data.py - pull REAL island data from Epic's Fortnite Data API and write
Excel-ready CSVs for the class project.

Run:  py fetch_data.py

Outputs (all UTF-8 with BOM so Excel shows emoji/accents correctly):
  islands_all.csv     every island pulled, including ones with null metrics
  islands_clean.csv   only islands with every metric present (the class dataset)
  excluded.csv        islands dropped from clean, and why
  daily_history.csv   7 days of daily metrics for the 10 biggest clean islands
  snapshots/<run_id>/ a copy of the CSVs from this run (report.py compares runs)
  raw/<run_id>/       every raw JSON response, unchanged (git-ignored)
  logs/               failed-call log and the printed summary for this run

How islands are chosen (no codes are typed in by hand except two Epic display names):
  1. GET /genres -> the 13 genres Epic uses for discovery.
  2. For each genre, GET /genres/{slug}/rankings (one hourly snapshot for all genres)
     and keep the islands at ranks 1, 10, 50, 150 and 400. Taking several ranks,
     not just the top ones, gives a spread from huge to small islands, which the
     histograms and terciles need.
  3. Epic-made experiences never appear in the genre rankings, and the API has no
     way to list them. The spec says Epic first-party modes can be looked up by a
     "displayName". Only the names in EPIC_DISPLAY_NAMES were found to work.
"""

import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from fortnite_api import AuthRequired, FortniteClient

sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles choke on emoji in titles

# ---------------------------------------------------------------- settings
SAMPLE_RANKS = [1, 10, 50, 150, 400]     # ranks taken from every genre leaderboard

# Epic first-party experiences, looked up by display name.
#   "battle-royale" is the example given in Epic's own API spec.
#   "reload" was tried because Reload was on the project brief, and the API confirmed
#   it (creatorCode "epic", code "experience_reload").
# Also tried and NOT found (404): zero-build, battle-royale-zero-build, og,
#   lego-fortnite, lego, festival, fortnite-festival-main-stage, ballistic,
#   blitz-royale, rocket-racing. Add a name here only after the API confirms it.
EPIC_DISPLAY_NAMES = ["battle-royale", "reload"]

# Genres grouped into 4 broader groups so each pivot row has several islands.
GENRE_GROUPS = {
    "battle-royale": "Combat & Competitive",
    "shooter": "Combat & Competitive",
    "strategy": "Combat & Competitive",
    "party-mini-games": "Casual & Party",
    "music-rhythm": "Casual & Party",
    "deathrun-platformer": "Casual & Party",
    "sports-racing": "Casual & Party",
    "adventure-rpg": "Adventure, Sim & Social",
    "simulation-tycoon": "Adventure, Sim & Social",
    "roleplaying-social": "Adventure, Sim & Social",
    "survival": "Survival & Horror",
    "horror": "Survival & Horror",
    "roguelike": "Survival & Horror",
}
EPIC_GROUP = "Epic-made (not ranked)"

# API metric name -> CSV column name. All values are for one complete UTC day.
METRICS = {
    "peakCCU": "peak_ccu_24h",
    "plays": "plays_24h",
    "uniquePlayers": "unique_players_24h",
    "minutesPlayed": "minutes_played_24h",
    "averageMinutesPerPlayer": "avg_minutes_per_player",
    "favorites": "favorites",
    "recommendations": "recommendations",
}
RETENTION = {"d1": "retention_d1", "d7": "retention_d7"}
METRIC_COLS = list(METRICS.values()) + list(RETENTION.values())
COUNT_COLS = ["peak_ccu_24h", "plays_24h", "unique_players_24h", "minutes_played_24h",
              "favorites", "recommendations"]
MAX_FAILURE_RATE = 0.05


# ---------------------------------------------------------------- helpers
def value_for_day(series, day_iso):
    """Return (value, status) for one day from a list of {value|d1|d7, timestamp}.
    status is 'ok', 'null' (API sent null) or 'missing' (no bucket for that day)."""
    for item in series or []:
        if item.get("timestamp", "")[:10] == day_iso:
            return item, "ok"
    return None, "missing"


def tercile_labels(series):
    """Low/Medium/High by the 33.3rd and 66.7th percentiles (pandas linear method).
    Low: value <= p33, Medium: p33 < value <= p67, High: value > p67."""
    p33, p67 = series.quantile([1 / 3, 2 / 3])
    labels = np.where(series <= p33, "Low", np.where(series <= p67, "Medium", "High"))
    return pd.Series(labels, index=series.index), float(p33), float(p67)


def safe_ratio(num, den):
    """num / den, blank (NaN) when either side is missing or the denominator is 0."""
    num = pd.to_numeric(num, errors="coerce")
    den = pd.to_numeric(den, errors="coerce")
    return (num / den.where(den > 0)).round(4)


def bin_counts(series, edges):
    """Count values in (edge[i], edge[i+1]] - the same rule Excel's histogram uses."""
    cats = pd.cut(series, bins=edges, include_lowest=True)
    return cats.value_counts(sort=False)


def nice_width(lo, hi, target_bins=10):
    for w in [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 15, 20, 25, 50, 100]:
        if (hi - lo) / w <= target_bins:
            return w
    return 100


def write_csv(df, name, run_dir):
    df.to_csv(name, index=False, encoding="utf-8-sig")
    df.to_csv(run_dir / name, index=False, encoding="utf-8-sig")


# ---------------------------------------------------------------- main
def main():
    pulled_at = datetime.now(timezone.utc).replace(microsecond=0)
    run_id = pulled_at.strftime("%Y%m%dT%H%M%SZ")
    pulled_at_iso = pulled_at.isoformat().replace("+00:00", "Z")

    # 7 complete UTC days: [today-7 00:00, today 00:00). The API rejects earlier starts.
    today = pulled_at.replace(hour=0, minute=0, second=0)
    window_from = today - timedelta(days=7)
    metrics_day = (today - timedelta(days=1)).date().isoformat()   # last complete day
    window = {"from": window_from.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
              "to": today.strftime("%Y-%m-%dT%H:%M:%S.000Z")}

    client = FortniteClient(run_id)
    print(f"Pull started {pulled_at_iso}. Metrics day = {metrics_day} (UTC). Window = {window}")

    # ---- 1. choose islands --------------------------------------------------
    sample = []   # dicts: code, genre, genre_rank, source
    genres = client.get("/genres")
    snapshot_at = None
    for g in (genres or {}).get("data", []):
        params = {"size": max(SAMPLE_RANKS)}
        if snapshot_at:
            params["at"] = snapshot_at          # same hourly snapshot for every genre
        ranking = client.get(f"/genres/{g['slug']}/rankings", params=params)
        if not ranking:
            continue
        snapshot_at = snapshot_at or ranking["meta"]["snapshot"]
        by_rank = {item["rank"]: item["islandCode"] for item in ranking["data"]}
        for r in SAMPLE_RANKS:
            if r in by_rank:
                sample.append({"code": by_rank[r], "genre": g["displayName"],
                               "genre_slug": g["slug"], "genre_rank": r, "source": "genre ranking"})
    for name in EPIC_DISPLAY_NAMES:
        sample.append({"code": name, "genre": None, "genre_slug": None,
                       "genre_rank": None, "source": "Epic display name"})
    print(f"Sampled {len(sample)} islands ({len(EPIC_DISPLAY_NAMES)} Epic display names). "
          f"Rankings snapshot: {snapshot_at}")

    # ---- 2. metadata + 7 days of daily metrics for each island ---------------
    rows, history = [], []
    for s in sample:
        meta = client.get(f"/islands/{s['code']}")
        metrics = client.get(f"/islands/{s['code']}/metrics/day", params=window)
        code = (meta or {}).get("code", s["code"])
        row = {
            "island_code": code,
            "title": (meta or {}).get("title"),
            "creator": (meta or {}).get("creatorCode"),
            "category": (meta or {}).get("category"),       # brand code; usually empty
            "created_in": (meta or {}).get("createdIn"),
            "tags": ";".join((meta or {}).get("tags") or []),
            "epic_made": "Yes" if (meta or {}).get("creatorCode") == "epic" else "No",
            "genre": s["genre"],
            "genre_group": GENRE_GROUPS.get(s["genre_slug"], "Other (unmapped)") if s["genre_slug"] else EPIC_GROUP,
            "genre_rank": s["genre_rank"],
            "selected_via": s["source"],
            "metrics_date": metrics_day,
        }
        problems = []
        if meta is None:
            problems.append("metadata call failed")
        if metrics is None:
            problems.append("metrics call failed")
        else:
            for api_name, col in METRICS.items():
                item, status = value_for_day(metrics.get(api_name), metrics_day)
                row[col] = item.get("value") if item else None
                if status == "missing":
                    problems.append(f"{col}: no bucket for {metrics_day}")
                elif row[col] is None:
                    problems.append(f"{col}: null from API")
            item, status = value_for_day(metrics.get("retention"), metrics_day)
            for key, col in RETENTION.items():
                row[col] = item.get(key) if item else None
                if status == "missing":
                    problems.append(f"{col}: no bucket for {metrics_day}")
                elif row[col] is None:
                    problems.append(f"{col}: null from API")
            # Keep every day for daily_history.csv
            days = sorted({x["timestamp"][:10] for x in metrics.get("peakCCU", [])})
            for d in days:
                ret, _ = value_for_day(metrics.get("retention"), d)
                history.append({
                    "island_code": code, "title": row["title"], "epic_made": row["epic_made"], "date": d,
                    "peak_ccu": (value_for_day(metrics.get("peakCCU"), d)[0] or {}).get("value"),
                    "plays": (value_for_day(metrics.get("plays"), d)[0] or {}).get("value"),
                    "unique_players": (value_for_day(metrics.get("uniquePlayers"), d)[0] or {}).get("value"),
                    "avg_minutes_per_player": (value_for_day(metrics.get("averageMinutesPerPlayer"), d)[0] or {}).get("value"),
                    "retention_d1": (ret or {}).get("d1"),
                    "retention_d7": (ret or {}).get("d7"),
                })
        row["pulled_at"] = pulled_at_iso
        row["_problems"] = "; ".join(problems)
        rows.append(row)

    # ---- 3. spot-check: combined endpoint vs single-metric endpoints ---------
    # We use /metrics/day (all metrics in one call, 8x fewer requests). To make sure
    # it reports the same numbers as the single-metric endpoints in the brief,
    # compare peak-ccu and retention for one Epic and one creator island.
    spot_checks = []
    for code in [r["island_code"] for r in rows if r["epic_made"] == "Yes"][:1] + \
                [r["island_code"] for r in rows if r["epic_made"] == "No"][:1]:
        combined = next(r for r in rows if r["island_code"] == code)
        single_ccu = client.get(f"/islands/{code}/metrics/day/peak-ccu", params=window)
        single_ret = client.get(f"/islands/{code}/metrics/day/retention", params=window)
        if single_ccu and single_ret:
            ccu_item, _ = value_for_day(single_ccu.get("intervals"), metrics_day)
            ret_item, _ = value_for_day(single_ret.get("intervals"), metrics_day)
            same = ((ccu_item or {}).get("value") == combined.get("peak_ccu_24h")
                    and (ret_item or {}).get("d1") == combined.get("retention_d1")
                    and (ret_item or {}).get("d7") == combined.get("retention_d7"))
            spot_checks.append(f"{code}: {'MATCH' if same else 'MISMATCH'}")
        else:
            spot_checks.append(f"{code}: could not check (call failed)")

    # ---- 4. stop if too many calls failed -----------------------------------
    fail_rate = client.failure_rate()
    if fail_rate > MAX_FAILURE_RATE:
        print(f"\n{len(client.failures)} of {client.calls} calls failed ({fail_rate:.1%}). "
              f"See {client.fail_log_path}")
        print("DATA INTEGRITY FAIL: do not use these results.")
        sys.exit(1)

    # ---- 5. build the tables ------------------------------------------------
    all_df = pd.DataFrame(rows)
    for c in COUNT_COLS + ["genre_rank"]:
        all_df[c] = pd.to_numeric(all_df[c], errors="coerce").astype("Int64")
    for c in ["avg_minutes_per_player", "retention_d1", "retention_d7"]:
        all_df[c] = pd.to_numeric(all_df[c], errors="coerce")

    all_df["plays_per_player"] = safe_ratio(all_df["plays_24h"], all_df["unique_players_24h"])
    all_df["favorite_rate"] = safe_ratio(all_df["favorites"], all_df["unique_players_24h"])
    all_df["recommend_rate"] = safe_ratio(all_df["recommendations"], all_df["unique_players_24h"])
    # Epic's spec: favorites/recommendations "are not supported for some Epic-made games,
    # so these fields will return 0". A 0 there means "not supported", not "nobody", so
    # the raw 0 is kept but the derived rate is left blank.
    epic = all_df["epic_made"] == "Yes"
    all_df.loc[epic & (all_df["favorites"] == 0), "favorite_rate"] = np.nan
    all_df.loc[epic & (all_df["recommendations"] == 0), "recommend_rate"] = np.nan

    dup_codes = all_df["island_code"][all_df["island_code"].duplicated()].tolist()
    is_clean = (all_df["_problems"] == "") & ~all_df["island_code"].duplicated()
    excluded = all_df.loc[~is_clean, ["island_code", "title", "genre", "_problems"]].rename(
        columns={"_problems": "reason"})
    excluded.loc[excluded["reason"] == "", "reason"] = "duplicate island code"

    clean = all_df[is_clean].copy()
    clean["ccu_tier"], ccu_p33, ccu_p67 = tercile_labels(clean["peak_ccu_24h"].astype(float))
    clean["retention_tier"], ret_p33, ret_p67 = tercile_labels(clean["retention_d1"])

    order = ["island_code", "title", "creator", "category", "created_in", "tags", "epic_made",
             "genre", "genre_group", "genre_rank", "selected_via", "metrics_date"] + METRIC_COLS + \
            ["plays_per_player", "favorite_rate", "recommend_rate"]
    clean = clean[order + ["ccu_tier", "retention_tier", "pulled_at"]]
    all_out = all_df[order + ["pulled_at"]].assign(problems=all_df["_problems"])

    hist = pd.DataFrame(history)
    top10 = clean.nlargest(10, "peak_ccu_24h")["island_code"].tolist()
    hist = hist[hist["island_code"].isin(top10)].sort_values(["island_code", "date"])
    for c in ["peak_ccu", "plays", "unique_players"]:
        hist[c] = pd.to_numeric(hist[c], errors="coerce").astype("Int64")

    run_dir = Path("snapshots") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    write_csv(all_out, "islands_all.csv", run_dir)
    write_csv(clean, "islands_clean.csv", run_dir)
    write_csv(excluded, "excluded.csv", run_dir)
    write_csv(hist, "daily_history.csv", run_dir)

    # ---- 6. summary + integrity checks --------------------------------------
    out = []
    p = out.append
    p("=" * 70)
    p(f"PULL SUMMARY  run {run_id}")
    p("=" * 70)
    p(f"pulled_at (UTC):            {pulled_at_iso}")
    p(f"metrics day (UTC):          {metrics_day}   (24h columns = this full UTC day)")
    p(f"rankings snapshot (UTC):    {snapshot_at}")
    p(f"API calls / HTTP requests:  {client.calls} / {client.http_requests}  (cap {client.max_requests})")
    p(f"failed calls:               {len(client.failures)} ({fail_rate:.1%})  -> {client.fail_log_path}")
    p(f"rows pulled (islands_all):  {len(all_out)}")
    p(f"rows in clean:              {len(clean)}   excluded: {len(excluded)}")
    p(f"duplicate island codes:     {dup_codes or 'none'}")
    p(f"combined-vs-single endpoint check: {', '.join(spot_checks) or 'not run'}")
    p("")
    p("Nulls per column in islands_all.csv (blank cells):")
    for c in METRIC_COLS + ["title", "creator", "category", "created_in", "tags"]:
        n = all_out[c].isna().sum() + (all_out[c] == "").sum() if all_out[c].dtype == object else all_out[c].isna().sum()
        p(f"  {c:<26}{int(n)}")
    p("")
    p("Clean rows by group:")
    for col in ["genre_group", "epic_made", "ccu_tier", "retention_tier"]:
        p(f"  {col}: " + ", ".join(f"{k}={v}" for k, v in clean[col].value_counts().items()))
    p("")
    p(f"Tercile cutoffs (clean rows): peak_ccu_24h p33={ccu_p33:,.1f}  p67={ccu_p67:,.1f}")
    p(f"                              retention_d1 p33={ret_p33:.4f}  p67={ret_p67:.4f}")

    # Suspicious-value checks (reported, never changed)
    sus = []
    num = all_out[METRIC_COLS].apply(pd.to_numeric, errors="coerce")
    for c in METRIC_COLS:
        n = int((num[c] < 0).sum())
        if n:
            sus.append(f"{n} negative value(s) in {c}")
    for c in RETENTION.values():
        bad = all_out.loc[(num[c] < 0) | (num[c] > 1), "island_code"].tolist()
        if bad:
            sus.append(f"{c} outside 0-1 for {bad}")
    d7_gt_d1 = all_out.loc[num["retention_d7"] > num["retention_d1"], "island_code"].tolist()
    if d7_gt_d1:
        sus.append(f"retention_d7 > retention_d1 (unusual, not impossible) for {len(d7_gt_d1)} island(s): {d7_gt_d1}")
    ccu_gt_players = all_out.loc[num["peak_ccu_24h"] > num["unique_players_24h"], "island_code"].tolist()
    if ccu_gt_players:
        sus.append(f"peak_ccu_24h > unique_players_24h (should be impossible): {ccu_gt_players}")
    conc = num["peak_ccu_24h"] / num["unique_players_24h"]
    # Only for islands with >= 1,000 players; tiny islands hit high ratios by chance.
    for _, r in all_out[(conc > 0.5) & (num["unique_players_24h"] >= 1000)].iterrows():
        sus.append(f"peak CCU is {conc[_]:.0%} of the day's unique players for {r.title} ({r.island_code}); "
                   "big islands are usually far lower (very long sessions, AFK play, or a metric issue?)")
    plays_lt_players = all_out.loc[num["plays_24h"] < num["unique_players_24h"], "island_code"].tolist()
    if plays_lt_players:
        sus.append(f"plays_24h < unique_players_24h (each player should have >= 1 play): {plays_lt_players}")
    implied = num["minutes_played_24h"] / num["unique_players_24h"]
    gap = (implied - num["avg_minutes_per_player"]).abs() / num["avg_minutes_per_player"]
    off = all_out.loc[gap > 0.05, "island_code"].tolist()
    if off:
        sus.append(f"avg_minutes_per_player differs >5% from minutes_played/unique_players (metric definition?): {off}")
    zero_fav = all_out.loc[(all_out["epic_made"] == "Yes") & ((num["favorites"] == 0) | (num["recommendations"] == 0)), "island_code"].tolist()
    if zero_fav:
        sus.append(f"Epic island(s) with favorites/recommendations = 0 ('not supported' per spec): {zero_fav}")
    logccu = np.log10(clean["peak_ccu_24h"].astype(float).clip(lower=1))
    q1, q3 = logccu.quantile([0.25, 0.75])
    outliers = clean.loc[(logccu > q3 + 1.5 * (q3 - q1)) | (logccu < q1 - 1.5 * (q3 - q1)), ["island_code", "title", "peak_ccu_24h"]]
    for _, r in outliers.iterrows():
        sus.append(f"peak_ccu outlier even on a log scale: {r.title} ({r.island_code}) = {int(r.peak_ccu_24h):,}")
    if mism := [s for s in spot_checks if "MISMATCH" in s]:
        sus.append(f"combined vs single-metric endpoint mismatch: {mism}")
    if len(clean) < 40:
        sus.append(f"only {len(clean)} clean rows; the class project needs at least 40")
    p("")
    p("Suspicious / worth a look:")
    for s in sus or ["nothing flagged"]:
        p(f"  - {s}")

    # Histogram help
    p("")
    p("Histogram help (clean rows):")
    hist_lines = []
    ccu = clean["peak_ccu_24h"].astype(float)
    log_edges = [0, 10, 30, 100, 300, 1_000, 3_000, 10_000, 30_000, 100_000, 300_000,
                 1_000_000, 3_000_000, 10_000_000, 30_000_000]
    log_edges = [e for e in log_edges if e < ccu.max()] + [next(e for e in log_edges if e >= ccu.max())]
    for name, s, edges in [
        ("peak_ccu_24h", ccu, log_edges),
        ("retention_d1", clean["retention_d1"], None),
        ("avg_minutes_per_player", clean["avg_minutes_per_player"], None),
    ]:
        if edges is None:
            w = nice_width(s.min(), s.max())
            lo = np.floor(s.min() / w) * w
            edges = list(np.round(np.arange(lo, s.max() + w, w), 4))
            if edges[-1] < s.max():
                edges.append(round(edges[-1] + w, 4))
            how = f"equal width {w}"
        else:
            how = "log-style 1-3-10 steps (peak CCU is very skewed)"
        hist_lines.append(f"  {name}: min={s.min():,.4g}  median={s.median():,.4g}  max={s.max():,.4g}  -> {how}")
        hist_lines.append(f"    bin upper edges for Excel: {', '.join(f'{e:g}' for e in edges[1:])}")
        counts = bin_counts(s, edges)
        hist_lines.append("    counts: " + ", ".join(f"<= {iv.right:g}: {n}" for iv, n in counts.items()))
    out.extend(hist_lines)
    p("=" * 70)

    text = "\n".join(out)
    print(text)
    Path("logs", f"summary_{run_id}.txt").write_text(text, encoding="utf-8")
    shutil.copy(Path("logs", f"summary_{run_id}.txt"), run_dir / "summary.txt")
    update_readme(pulled_at_iso, metrics_day, snapshot_at, len(all_out), len(clean),
                  ccu_p33, ccu_p67, ret_p33, ret_p67, hist_lines, len(client.failures), client.calls)


def update_readme(pulled_at, metrics_day, snapshot_at, n_all, n_clean,
                  c33, c67, r33, r67, hist_lines, n_fail, n_calls):
    """Rewrite the auto-generated block of README.md with this run's facts."""
    path = Path("README.md")
    if not path.exists():
        return
    start, end = "<!-- AUTO-GENERATED:START -->", "<!-- AUTO-GENERATED:END -->"
    text = path.read_text(encoding="utf-8")
    if start not in text or end not in text:
        return
    block = f"""{start}
_This block is rewritten by `fetch_data.py` on every run._

| Item | Value |
|---|---|
| Pull date/time (UTC) | {pulled_at} |
| Metrics day (the "24h" columns) | {metrics_day} 00:00 to 24:00 UTC |
| Genre-rankings snapshot used to pick islands | {snapshot_at} |
| Islands pulled / clean | {n_all} / {n_clean} |
| Failed API calls | {n_fail} of {n_calls} |

**Tier cutoffs used in this pull** (terciles of the clean rows, pandas linear percentiles):

| Column | Low | Medium | High |
|---|---|---|---|
| ccu_tier (peak_ccu_24h) | <= {c33:,.1f} | > {c33:,.1f} and <= {c67:,.1f} | > {c67:,.1f} |
| retention_tier (retention_d1) | <= {r33:.4f} | > {r33:.4f} and <= {r67:.4f} | > {r67:.4f} |

**Histogram help**
```
{chr(10).join(hist_lines)}
```
{end}"""
    before = text.split(start)[0]
    after = text.split(end)[1]
    path.write_text(before + block + after, encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except AuthRequired as exc:
        print(exc)
        sys.exit(2)
