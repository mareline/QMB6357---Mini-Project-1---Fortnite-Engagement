# QMB6357 - Mini-Project 1 - Fortnite Engagement

This project pulls real engagement data for Fortnite islands from Epic's public Fortnite Data API and turns it
into CSV files I can open in Excel. Each island gets its peak number of players online at once, how many times
it was played, how long people stayed, and how many came back the next day and the next week. I used it for my
business statistics mini-project. I also used it to practice the kind of work a product manager on Fortnite's
engagement team might do.

Every number in the data came straight from Epic's API. I didn't type in, estimate or fill in any values. The
original API responses are saved in a `raw/` folder so the numbers can be checked.

## What the assignment is for

The mini-project asks for a real dataset of at least 40 rows and at least 7 columns, with a mix of numbers and
text. I then analyze it in Excel with pivot tables, charts and histograms. The point is to practice the full
process of working with data. That means collecting it, cleaning it, describing it, and saying what it can and
can't tell you. Most of the work isn't fancy math. It's being careful about where the numbers came from and what
they mean.

I picked Fortnite because I'm preparing for a product management internship on Fortnite's engagement team. The
questions a PM there would ask fit a stats class well. Which kinds of islands keep players coming back? How
uneven is popularity? Do bigger islands also have better retention? Using real data also means real problems,
like missing values, odd outliers and limits on what the API shares. That's more useful practice than a
cleaned-up textbook dataset.

This README covers only the data and how I collected it. My analysis, pivot tables, charts and conclusions are
in my Excel file.

## How to run it

```
py -m pip install -r requirements.txt
py fetch_data.py        # pulls the data, writes the CSVs, prints a data-quality summary
```

The other scripts are optional extras for the interview side of the project (see the end of this README).
On Windows, if island titles with emoji cause an error in the console, run `set PYTHONIOENCODING=utf-8` first.
No API key is needed.

## Files

| File | What it is |
|---|---|
| `islands_clean.csv` | **My class dataset.** One row per island, only islands with every value present. |
| `islands_all.csv` | Every island I pulled, including the incomplete ones, with a `problems` column. |
| `excluded.csv` | Which islands I dropped from the clean file and why. |
| `daily_history.csv` | Seven days of daily numbers for the 10 biggest islands, for a line chart. |
| `snapshots/` | A saved copy of the CSVs from each run, so pulls can be compared later. |
| `raw/` | The original API responses (kept on my computer, not uploaded to GitHub). |
| `logs/` | A record of every API call that failed and why, plus the summary from each run. |

The CSVs are saved so Excel shows emoji and accented letters correctly. Numbers have no commas. Dates look like
`2026-11-15`. A blank cell means there was no value, not zero.

## Data collection plan

**What I collected.** I collected basic details for each island (title, creator, tags, genre). I also collected
one full day of engagement numbers: peak players online at once, plays, unique players, total minutes played,
average minutes per player, favorites, recommendations, and day-1 and day-7 retention. For the 10 biggest
islands I also kept the last seven days.

**Why.** I wanted to compare engagement across different kinds of islands. That includes genre, size, how well
an island keeps players, and whether Epic made it or an outside creator did.

**How.** A Python script (`fetch_data.py`) asks the API for the data, island by island:

1. It gets Epic's list of 13 genres (Shooter, Horror, Party & Mini Games, and so on).
2. For each genre it gets Epic's leaderboard and takes the islands ranked **1, 10, 50, 150 and 400**. All
   genres are read at the same hour so the lists are comparable. That gives 65 creator-made islands.
3. It adds two Epic-made modes, **Battle Royale** and **Reload**. I explain why only two below.
4. For each island it gets the island's details and seven days of daily numbers in one request.
5. It keeps the most recent complete day (midnight to midnight, UTC time) for the main columns.

**When.** I ran the pull by hand. The exact date and time is in the table below and in the `pulled_at` column
of every row. Running the script again on a later day adds a new snapshot.

<!-- AUTO-GENERATED:START -->
_This block is rewritten by `fetch_data.py` on every run._

| Item | Value |
|---|---|
| Pull date/time (UTC) | 2026-11-16T23:35:11Z |
| Metrics day (the "24h" columns) | 2026-11-15 00:00 to 24:00 UTC |
| Genre-rankings snapshot used to pick islands | 2026-11-16T23:00:00.000Z |
| Islands pulled / clean | 67 / 56 |
| Failed API calls | 4 of 152 |

**Tier cutoffs used in this pull** (terciles of the clean rows, pandas linear percentiles):

| Column | Low | Medium | High |
|---|---|---|---|
| ccu_tier (peak_ccu_24h) | <= 48.0 | > 48.0 and <= 490.7 | > 490.7 |
| retention_tier (retention_d1) | <= 0.1133 | > 0.1133 and <= 0.2600 | > 0.2600 |

**Histogram help**
```
  peak_ccu_24h: min=2  median=258.5  max=3.774e+06  -> log-style 1-3-10 steps (peak CCU is very skewed)
    bin upper edges for Excel: 10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000, 300000, 1e+06, 3e+06, 1e+07
    counts: <= 10: 7, <= 30: 9, <= 100: 7, <= 300: 6, <= 1000: 10, <= 3000: 4, <= 10000: 6, <= 30000: 3, <= 100000: 2, <= 300000: 1, <= 1e+06: 0, <= 3e+06: 0, <= 1e+07: 1
  retention_d1: min=0  median=0.17  max=0.82  -> equal width 0.1
    bin upper edges for Excel: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9
    counts: <= 0.1: 17, <= 0.2: 12, <= 0.3: 16, <= 0.4: 7, <= 0.5: 2, <= 0.6: 0, <= 0.7: 0, <= 0.8: 1, <= 0.9: 1
  avg_minutes_per_player: min=6.25  median=24.33  max=105.7  -> equal width 10
    bin upper edges for Excel: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110
    counts: <= 10: 5, <= 20: 18, <= 30: 15, <= 40: 9, <= 50: 5, <= 60: 2, <= 70: 0, <= 80: 0, <= 90: 0, <= 100: 1, <= 110: 1
```