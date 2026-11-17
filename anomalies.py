"""
anomalies.py - PROTOTYPE. Flags days where an island's plays, peak CCU or
retention fall far outside that island's OWN earlier days in daily_history.csv.

Run after fetch_data.py:  py anomalies.py
Writes anomalies.csv (every check, with its outcome) and anomalies.md (readable summary).

IMPORTANT: 7 days of history is far too short for strong conclusions. A "flag"
here means "a human should look at this", not "something is wrong".

How each (island, metric, day) is judged, in this order:
  1. Data checks first - if any fails, the result is "cannot judge", never a flag:
       a. the day row is missing from the history
       b. the value, or too many earlier values, is null (Epic returns null when an
          island had fewer than 5 unique players, so a null is not a zero)
       c. fewer than MIN_BASELINE earlier days have a value
       d. retention outside 0-1 (would mean a unit/definition problem)
       e. retention so small that the 2-decimal rounding in the API is bigger than
          any change we could detect (baseline median below 0.05)
  2. Then compare the day with the earlier days of the same island:
       baseline = median of earlier days, spread = MAD (median absolute deviation)
       robust z = (value - baseline) / (1.4826 * MAD)
     Flag only if BOTH |robust z| >= Z_LIMIT AND the move is big in plain terms
     (>= MIN_REL_CHANGE for counts, >= MIN_RET_POINTS for retention).
  3. Then add context to each flag, so island problems are separated from
     ecosystem-wide or calendar effects:
       - "shared move": many islands flagged the same way on the same day
       - "weekend": a Saturday/Sunday compared with mostly weekday days
       - "island-specific": neither of the above
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

METRICS = ["plays", "peak_ccu", "retention_d1", "retention_d7"]
MIN_BASELINE = 3        # need at least 3 earlier days to compare against
Z_LIMIT = 3.5           # common robust-z cut-off for "far outside"
MIN_REL_CHANGE = 0.30   # counts must also move by at least 30% vs baseline
MIN_RET_POINTS = 0.05   # retention must also move by at least 5 percentage points
RET_PRECISION_FLOOR = 0.05
SHARED_SHARE = 0.3      # if >= 30% of islands move the same way the same day, call it a shared move


def check(series, idx, metric):
    """Judge one day (position idx) of one island's metric series. Returns dict."""
    value = series.iloc[idx]
    earlier = series.iloc[:idx]
    res = {"value": value, "baseline_median": np.nan, "robust_z": np.nan, "change": np.nan}

    if pd.isna(value):
        return {**res, "status": "cannot judge", "reason": "value is null (possible <5-player rule or missing data)"}
    if earlier.notna().sum() < MIN_BASELINE:
        return {**res, "status": "cannot judge",
                "reason": f"fewer than {MIN_BASELINE} earlier non-null days (nulls = possible <5-player rule)"}
    is_ret = metric.startswith("retention")
    if is_ret and not (0 <= value <= 1):
        return {**res, "status": "data problem", "reason": "retention outside 0-1: check unit/definition"}

    earlier = earlier.dropna()
    base = earlier.median()
    mad = (earlier - base).abs().median()
    res["baseline_median"] = base
    if is_ret and base < RET_PRECISION_FLOOR:
        return {**res, "status": "cannot judge", "reason": "retention too small for 2-decimal API precision"}

    z = (value - base) / (1.4826 * mad) if mad > 0 else (np.inf if value != base else 0.0)
    res["robust_z"] = round(z, 2) if np.isfinite(z) else z
    if is_ret:
        change = value - base
        big = abs(change) >= MIN_RET_POINTS
    else:
        change = (value / base - 1) if base else np.nan
        big = pd.notna(change) and abs(change) >= MIN_REL_CHANGE
    res["change"] = round(change, 3) if pd.notna(change) else change
    if abs(z) >= Z_LIMIT and big:
        direction = "above" if value > base else "below"
        return {**res, "status": "FLAG", "reason": f"far {direction} its own earlier days"}
    return {**res, "status": "normal", "reason": ""}


def main():
    h = pd.read_csv("daily_history.csv", encoding="utf-8-sig", parse_dates=["date"])
    all_dates = sorted(h["date"].unique())
    results = []

    for code, g in h.groupby("island_code"):
        # Re-index on the full date list so a missing day shows up as a missing row.
        g = g.set_index("date").reindex(all_dates)
        title = g["title"].dropna().iloc[0]
        for metric in METRICS:
            s = g[metric]
            for idx, day in enumerate(all_dates):
                if idx < MIN_BASELINE:
                    continue  # the first days have nothing earlier to compare with
                if pd.isna(g["title"].iloc[idx]):
                    r = {"value": np.nan, "status": "cannot judge", "reason": "day missing from history"}
                else:
                    r = check(s, idx, metric)
                results.append({"island_code": code, "title": title, "metric": metric,
                                "date": pd.Timestamp(day).date().isoformat(),
                                "weekday": pd.Timestamp(day).day_name(), **r})

    res = pd.DataFrame(results)

    # Context check: is the move specific to this island, or did many islands move
    # the same way on the same day (weekend, live event, season change, outage)?
    n_islands = h["island_code"].nunique()
    res["direction"] = np.sign(res["change"]).where(res["status"] == "FLAG")
    same_day = (res[res["status"] == "FLAG"].groupby(["date", "metric", "direction"])["island_code"]
                .nunique().rename("islands_same_move"))
    res = res.merge(same_day, on=["date", "metric", "direction"], how="left")
    res["context"] = ""
    shared = (res["status"] == "FLAG") & (res["islands_same_move"] >= SHARED_SHARE * n_islands)
    res.loc[shared, "context"] = "shared move: many islands moved the same way that day (ecosystem/calendar effect?)"
    weekend_no_base = (res["status"] == "FLAG") & res["weekday"].isin(["Saturday", "Sunday"]) & ~shared
    res.loc[weekend_no_base, "context"] = "weekend day compared with mostly weekday baseline"
    res.loc[(res["status"] == "FLAG") & (res["context"] == ""), "context"] = "island-specific"
    res = res.drop(columns=["direction"])
    res.to_csv("anomalies.csv", index=False, encoding="utf-8-sig")

    flags = res[res["status"] == "FLAG"]
    specific = flags[flags["context"] == "island-specific"]
    explained = flags[flags["context"] != "island-specific"]
    cannot = res[~res["status"].isin(["FLAG", "normal"])]

    out = []
    p = out.append
    p("# Anomaly check (PROTOTYPE)")
    p("")
    p(f"Data: daily_history.csv, {h['island_code'].nunique()} islands, "
      f"{pd.Timestamp(all_dates[0]).date()} to {pd.Timestamp(all_dates[-1]).date()} (UTC days).")
    p("")
    p("> **7 days of history is too short for strong conclusions.** Each day is compared with only "
      "3 to 6 earlier days, there is no weekly pattern to compare against, and one weekend or one "
      "in-game event can look like an anomaly. Treat every flag as a question, not an answer.")
    p("")
    p(f"Checks run: {len(res)} (island x metric x day, days 4-7). Flags: **{len(flags)}** "
      f"({len(specific)} island-specific, {len(explained)} with a broader explanation). "
      f"Could not judge: {len(cannot)}.")
    p("")

    def line(r):
        unit = f"{r.change:+.0%}" if not r.metric.startswith("retention") else f"{r.change * 100:+.0f} pts"
        return (f"- **{r.title}**: `{r.metric}` on {r.date} ({r.weekday}) = {r.value:,.4g} vs earlier median "
                f"{r.baseline_median:,.4g} ({unit}, robust z {r.robust_z})")

    p("## Island-specific flags (look at these first)")
    p("Only this island moved this way on this day, on a weekday.")
    p("")
    for _, r in specific.iterrows():
        p(line(r))
    if specific.empty:
        p("None.")
    p("")
    p("## Flags with a broader explanation (probably not about the island itself)")
    p(f"'Shared move' = at least {SHARED_SHARE:.0%} of the {n_islands} islands were flagged in the same "
      "direction on the same day. 'Weekend' = Saturday/Sunday compared with earlier days that are mostly weekdays.")
    p("")
    for ctx, grp in explained.groupby("context"):
        p(f"**{ctx}**")
        p("")
        for _, r in grp.iterrows():
            p(line(r))
        p("")
    if explained.empty:
        p("None.")
    p("")
    p("Before acting on a flag, check:")
    p("- **Calendar effects:** is it a weekend, holiday, or the start/end of a Fortnite season or live event?")
    p("- **Metric definitions:** `plays` counts every session start (re-queues inflate it); retention is "
      "returned as a 0-1 fraction rounded to 2 decimals although Epic's spec describes it as a 'number of players'.")
    p("- **Data gaps:** nulls mean fewer than 5 unique players; a day that is null is skipped, never treated as 0.")
    p("")
    p("## Could not judge (data issues, not anomalies)")
    if cannot.empty:
        p("None.")
    else:
        summary = cannot.groupby(["reason"]).size().reset_index(name="checks")
        for _, r in summary.iterrows():
            p(f"- {r.reason}: {r.checks} check(s)")
    Path("anomalies.md").write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote anomalies.md / anomalies.csv: {len(flags)} flag(s), {len(cannot)} cannot-judge, {len(res)} checks")


if __name__ == "__main__":
    main()
