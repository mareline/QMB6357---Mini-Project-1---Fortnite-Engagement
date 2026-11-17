"""
projection.py - PROTOTYPE. A plain "what range is plausible next week?" view of
peak concurrent players (peak CCU) for the islands in daily_history.csv.

Run after fetch_data.py:  py projection.py
Writes projection.csv (one row per island per future day) and projection.md.

THIS IS NOT A PREDICTION. It answers one narrow question:
  "If next week looks like the last 7 days, what range would daily peak CCU fall in?"

Method (deliberately simple so it can be explained in one sentence each):
  low     = the lowest daily peak CCU in the last 7 days
  typical = the median daily peak CCU in the last 7 days
  high    = the highest daily peak CCU in the last 7 days
The same range is used for each of the next 7 days. No trend is extrapolated,
because 7 points cannot separate a real trend from noise or a one-off event.
"""

import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

HORIZON_DAYS = 7
MIN_DAYS = 5      # skip islands with fewer than 5 non-null days of history
SHIFT_RATIO = 3   # last-2-day median >= 3x (or <= 1/3) first-half median -> level-shift warning

ASSUMPTIONS = [
    "Next week behaves like the last 7 days: no new season, patch, live event, featured "
    "placement, creator update or outage that the last 7 days did not already contain.",
    "Each day's peak is drawn from the same range as last week; weekday/weekend patterns "
    "are not modelled (7 days contain only one weekend).",
    "If last week contained a one-off spike (for example a live event), the 'high' end "
    "includes it and is probably too optimistic for a normal week.",
    "Nulls (Epic hides values when fewer than 5 unique players) are left out, never treated as 0.",
    "The range covers only what was observed. Real values can and will fall outside it.",
]


def main():
    h = pd.read_csv("daily_history.csv", encoding="utf-8-sig", parse_dates=["date"])
    last_day = h["date"].max()
    future = pd.date_range(last_day + pd.Timedelta(days=1), periods=HORIZON_DAYS, freq="D")

    rows, summary, skipped = [], [], []
    for code, g in h.groupby("island_code"):
        s = g.sort_values("date")["peak_ccu"].dropna()
        title = g["title"].iloc[0]
        if len(s) < MIN_DAYS:
            skipped.append(f"{title} ({len(s)} non-null days)")
            continue
        low, typ, high = int(s.min()), int(s.median()), int(s.max())
        latest = int(s.iloc[-1])
        # Sanity check on the core assumption: if the island's level jumped (or collapsed)
        # within the week, "next week looks like last week" is already false.
        early = s.iloc[: len(s) // 2].median()
        late = s.iloc[-2:].median()
        shift = early > 0 and (late / early >= SHIFT_RATIO or late / early <= 1 / SHIFT_RATIO)
        warning = (f"LEVEL SHIFT: last 2 days are {late / early:.1f}x the first half of the week; "
                   "range is not meaningful") if shift else ""
        summary.append({"island": title, "island_code": code, "latest_day": latest,
                        "low": low, "typical": typ, "high": high,
                        "range_width_pct_of_typical": round((high - low) / typ * 100, 1) if typ else None,
                        "warning": warning})
        for d in future:
            rows.append({"island_code": code, "title": title, "date": d.date().isoformat(),
                         "peak_ccu_low": low, "peak_ccu_typical": typ, "peak_ccu_high": high,
                         "warning": warning, "label": "PROTOTYPE range, not a prediction"})

    proj = pd.DataFrame(rows)
    proj.to_csv("projection.csv", index=False, encoding="utf-8-sig")
    summ = pd.DataFrame(summary).sort_values("typical", ascending=False)

    out = []
    p = out.append
    p("# Peak CCU range for the next 7 days (PROTOTYPE, not a prediction)")
    p("")
    p(f"Based on {h['date'].min().date()} to {last_day.date()} (UTC). "
      f"Range shown for {future[0].date()} to {future[-1].date()}.")
    p("")
    p("| Island | Latest day | Low | Typical (median) | High | Range width (% of typical) | Warning |")
    p("|---|---|---|---|---|---|---|")
    for _, r in summ.iterrows():
        p(f"| {r.island} | {r.latest_day:,} | {r.low:,} | {r.typical:,} | {r.high:,} | "
          f"{r.range_width_pct_of_typical}% | {r.warning} |")
    p("")
    p(f"A LEVEL SHIFT warning means the median of the last 2 days is at least {SHIFT_RATIO}x (or at most "
      f"1/{SHIFT_RATIO}) the median of the first half of the week. The island changed during the week "
      "(breakout, feature, update), so last week's range says little about next week.")
    p("")
    p("## Assumptions (read before using)")
    for a in ASSUMPTIONS:
        p(f"- {a}")
    if skipped:
        p("")
        p("Skipped (not enough non-null days): " + ", ".join(skipped))
    p("")
    p("_How to use in a PM conversation: 'If nothing changes, we would expect daily peak CCU somewhere "
      "between low and high. A day outside that range is a signal to investigate, not a forecast miss.'_")
    Path("projection.md").write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote projection.md / projection.csv for {len(summ)} islands ({len(skipped)} skipped)")


if __name__ == "__main__":
    main()
