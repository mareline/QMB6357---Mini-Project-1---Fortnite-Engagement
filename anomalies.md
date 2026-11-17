# Anomaly check (PROTOTYPE)

Data: daily_history.csv, 10 islands, 2026-11-09 to 2026-11-15 (UTC days).

> **7 days of history is too short for strong conclusions.** Each day is compared with only 3 to 6 earlier days, there is no weekly pattern to compare against, and one weekend or one in-game event can look like an anomaly. Treat every flag as a question, not an answer.

Checks run: 160 (island x metric x day, days 4-7). Flags: **37** (5 island-specific, 32 with a broader explanation). Could not judge: 4.

## Island-specific flags (look at these first)
Only this island moved this way on this day, on a weekday.

- **2233 ⭐ HARD PARKOUR DEATHRUN باركور**: `plays` on 2026-11-12 (Thursday) = 932 vs earlier median 1,632 (-43%, robust z -3.69)
- **Break The Egg**: `peak_ccu` on 2026-11-12 (Thursday) = 119 vs earlier median 186 (-36%, robust z -5.65)
- **Break The Egg**: `peak_ccu` on 2026-11-13 (Friday) = 4,842 vs earlier median 182 (+2560%, robust z 299.35)
- **Battle Royale**: `retention_d7` on 2026-11-13 (Friday) = 0.48 vs earlier median 0.545 (-6 pts, robust z -4.38)
- **Reload**: `peak_ccu` on 2026-11-13 (Friday) = 7.439e+04 vs earlier median 5.567e+04 (+34%, robust z 6.02)

## Flags with a broader explanation (probably not about the island itself)
'Shared move' = at least 30% of the 10 islands were flagged in the same direction on the same day. 'Weekend' = Saturday/Sunday compared with earlier days that are mostly weekdays.

**shared move: many islands moved the same way that day (ecosystem/calendar effect?)**

- **Piece Control 2v2 🎯**: `plays` on 2026-11-13 (Friday) = 1.656e+06 vs earlier median 1.217e+06 (+36%, robust z 4.81)
- **Piece Control 2v2 🎯**: `plays` on 2026-11-14 (Saturday) = 2.329e+06 vs earlier median 1.255e+06 (+86%, robust z 5.88)
- **Piece Control 2v2 🎯**: `peak_ccu` on 2026-11-14 (Saturday) = 3.144e+04 vs earlier median 1.604e+04 (+96%, robust z 4.52)
- **BOX PVP**: `plays` on 2026-11-13 (Friday) = 1.201e+06 vs earlier median 8.893e+05 (+35%, robust z 3.7)
- **BOX PVP**: `plays` on 2026-11-14 (Saturday) = 1.54e+06 vs earlier median 9.459e+05 (+63%, robust z 3.52)
- **BOX PVP**: `retention_d1` on 2026-11-13 (Friday) = 0.22 vs earlier median 0.28 (-6 pts, robust z -4.05)
- **CRAZY RED VS BLUE 🔴🔵**: `plays` on 2026-11-14 (Saturday) = 4.465e+05 vs earlier median 2.278e+05 (+96%, robust z 5.07)
- **CRAZY RED VS BLUE 🔴🔵**: `plays` on 2026-11-15 (Sunday) = 3.81e+05 vs earlier median 2.424e+05 (+57%, robust z 5.67)
- **CRAZY RED VS BLUE 🔴🔵**: `peak_ccu` on 2026-11-14 (Saturday) = 9,272 vs earlier median 5,540 (+67%, robust z 4.24)
- **CRAZY RED VS BLUE 🔴🔵**: `peak_ccu` on 2026-11-15 (Sunday) = 8,978 vs earlier median 5,837 (+54%, robust z 4.01)
- **2233 ⭐ HARD PARKOUR DEATHRUN باركور**: `plays` on 2026-11-15 (Sunday) = 6.824e+04 vs earlier median 1,426 (+4686%, robust z 149.48)
- **2233 ⭐ HARD PARKOUR DEATHRUN باركور**: `peak_ccu` on 2026-11-15 (Sunday) = 8,441 vs earlier median 69 (+12133%, robust z 564.68)
- **Bed Wars**: `retention_d1` on 2026-11-13 (Friday) = 0.24 vs earlier median 0.31 (-7 pts, robust z -4.72)
- **PILLARS**: `retention_d1` on 2026-11-13 (Friday) = 0.25 vs earlier median 0.33 (-8 pts, robust z -5.4)
- **GO UP FOR BRAINROTS**: `plays` on 2026-11-13 (Friday) = 1.099e+06 vs earlier median 8.386e+05 (+31%, robust z 6.23)
- **GO UP FOR BRAINROTS**: `plays` on 2026-11-14 (Saturday) = 1.894e+06 vs earlier median 8.483e+05 (+123%, robust z 19.14)
- **GO UP FOR BRAINROTS**: `plays` on 2026-11-15 (Sunday) = 1.607e+06 vs earlier median 8.668e+05 (+85%, robust z 8.33)
- **GO UP FOR BRAINROTS**: `peak_ccu` on 2026-11-14 (Saturday) = 2.582e+05 vs earlier median 1.657e+04 (+1459%, robust z 744.28)
- **GO UP FOR BRAINROTS**: `peak_ccu` on 2026-11-15 (Sunday) = 2.156e+05 vs earlier median 1.66e+04 (+1198%, robust z 227.85)
- **Break The Egg**: `plays` on 2026-11-13 (Friday) = 8.213e+04 vs earlier median 4,205 (+1853%, robust z 290.39)
- **Break The Egg**: `plays` on 2026-11-14 (Saturday) = 1.569e+05 vs earlier median 4,225 (+3615%, robust z 284.55)
- **Break The Egg**: `plays` on 2026-11-15 (Sunday) = 1.353e+05 vs earlier median 4,419 (+2963%, robust z 223.57)
- **Break The Egg**: `peak_ccu` on 2026-11-14 (Saturday) = 5,295 vs earlier median 186 (+2747%, robust z 265.07)
- **Break The Egg**: `peak_ccu` on 2026-11-15 (Sunday) = 6,285 vs earlier median 192.5 (+3165%, robust z 93.39)
- **Battle Royale**: `plays` on 2026-11-14 (Saturday) = 2.471e+08 vs earlier median 1.692e+08 (+46%, robust z 4.69)
- **Battle Royale**: `peak_ccu` on 2026-11-14 (Saturday) = 6.364e+06 vs earlier median 2.338e+06 (+172%, robust z 80.05)
- **Battle Royale**: `peak_ccu` on 2026-11-15 (Sunday) = 3.774e+06 vs earlier median 2.343e+06 (+61%, robust z 11.2)
- **Reload**: `plays` on 2026-11-15 (Sunday) = 8.938e+06 vs earlier median 5.393e+06 (+66%, robust z 3.79)
- **Reload**: `peak_ccu` on 2026-11-14 (Saturday) = 8.607e+04 vs earlier median 5.723e+04 (+50%, robust z 4.64)

**weekend day compared with mostly weekday baseline**

- **GO UP FOR BRAINROTS**: `retention_d7` on 2026-11-15 (Sunday) = 0.65 vs earlier median 0.52 (+13 pts, robust z 5.85)
- **Break The Egg**: `retention_d1` on 2026-11-14 (Saturday) = 0.52 vs earlier median 0.34 (+18 pts, robust z 4.05)
- **Break The Egg**: `retention_d7` on 2026-11-14 (Saturday) = 0.26 vs earlier median 0.11 (+15 pts, robust z 10.12)


Before acting on a flag, check:
- **Calendar effects:** is it a weekend, holiday, or the start/end of a Fortnite season or live event?
- **Metric definitions:** `plays` counts every session start (re-queues inflate it); retention is returned as a 0-1 fraction rounded to 2 decimals although Epic's spec describes it as a 'number of players'.
- **Data gaps:** nulls mean fewer than 5 unique players; a day that is null is skipped, never treated as 0.

## Could not judge (data issues, not anomalies)
- fewer than 3 earlier non-null days (nulls = possible <5-player rule): 1 check(s)
- value is null (possible <5-player rule or missing data): 3 check(s)