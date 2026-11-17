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
<!-- AUTO-GENERATED:END -->

## Why I made the choices I did

**Why several ranks instead of just the top islands.** If I only took the #1 island in each genre, every
island would be huge and the histograms would show almost nothing. Taking ranks 1, 10, 50, 150 and 400 gives
islands from a few players up to millions, so the data shows how uneven popularity really is. It's not a random
sample, though, so averages from it aren't "typical Fortnite" numbers.

**Why I didn't pick islands myself.** Choosing islands I already knew would bias the data toward famous ones.
Using Epic's own leaderboards at fixed ranks is a rule anyone could repeat and get the same list for that hour.

**Why only two Epic-made islands.** Epic's own modes never show up on the genre leaderboards, and the API has no
way to list them. The only way to look one up is by its exact name. "battle-royale" is the example in Epic's own
documentation, and "reload" also worked. Other names I tried (Zero Build, OG, LEGO Fortnite, Festival, Ballistic
and a few variations) didn't. I didn't want to guess codes, so I stopped there. Because there are only two, any
Epic-vs-creator comparison is weak, and I treat it that way.

**Why one full day instead of "the last 24 hours".** The API reports by calendar day in UTC time, and today's
numbers are still filling in. Using the last complete day means every island is measured over the same 24
hours.

**Why I dropped incomplete islands instead of filling them in.** Epic hides an island's numbers (shows a blank)
when fewer than 5 people played it that day. A blank doesn't mean zero. It means "too few to report." If I filled
those with 0 or an average, I'd be making up data. So those islands go into `excluded.csv` with the reason. The
clean file still has 56 islands, well over the 40-row minimum.

**Why Low / Medium / High tiers by thirds.** Pivot tables need text categories with at least three levels. I
split islands into thirds (terciles) by peak players and by day-1 retention. Splitting by thirds means each
group gets about the same number of islands. It also keeps the cutoffs tied to the data instead of picking round
numbers that might put almost everything in one group. The exact cutoffs are in the table above.

**Why genre groups.** Thirteen genres with about five islands each is too thin for a pivot table. I combined
them into four groups of similar games, so each group has 11 to 17 islands.

**Why a log-style histogram for peak players.** Peak players runs from 2 to almost 4 million. Equal-width bins
would put nearly every island in the first bar. Bins that grow by steps (10, 30, 100, 300, 1,000, and so on) show
the shape much better. Retention and average minutes are more even, so normal equal-width bins work for those.

**Why the API's own numbers and not a cleaner source.** Third-party Fortnite stats sites exist, but I can't
check how they collect or adjust their numbers. Going to Epic's API directly, and saving every response, means
each value can be traced back to its source.

## Data dictionary (`islands_clean.csv`)

| Column | Type | Unit / values | Where it comes from |
|---|---|---|---|
| island_code | text | e.g. `1234-5678-9012`; Epic modes look like `experience_br` | island details |
| title | text | island name | island details |
| creator | text | creator's code; `epic` for Epic-made | island details |
| category | text | a **brand** (e.g. LEGO, TMNT), blank for most islands | island details |
| created_in | text | `UEFN` or `FNC` (the two tools for building islands) | island details |
| tags | text | creator's tags, separated by `;` | island details |
| epic_made | text | Yes / No | derived from creator |
| genre | text | the Epic genre leaderboard the island came from; blank for Epic modes | genre leaderboard |
| genre_group | text | one of 4 groups, or `Epic-made (not ranked)` | derived (mapping below) |
| genre_rank | whole number | rank on that leaderboard | genre leaderboard |
| selected_via | text | `genre ranking` or `Epic display name` | how I picked it |
| metrics_date | date | the day all the daily numbers are for (UTC) | |
| peak_ccu_24h | whole number | most players online at the same moment | daily metrics |
| plays_24h | whole number | times the island was started (one player can count several times) | daily metrics |
| unique_players_24h | whole number | different players | daily metrics |
| minutes_played_24h | whole number | total minutes, all players | daily metrics |
| avg_minutes_per_player | decimal | minutes per player | daily metrics |
| favorites | whole number | times added to favorites that day | daily metrics |
| recommendations | whole number | times recommended that day | daily metrics |
| retention_d1 | decimal | share who came back, 0 to 1 (0.17 = 17%) | daily metrics |
| retention_d7 | decimal | share retained over 7 days, 0 to 1 | daily metrics |
| plays_per_player | decimal | plays ÷ unique players | calculated |
| favorite_rate | decimal | favorites ÷ unique players | calculated |
| recommend_rate | decimal | recommendations ÷ unique players | calculated |
| ccu_tier | text | Low / Medium / High by thirds of peak_ccu_24h | calculated |
| retention_tier | text | Low / Medium / High by thirds of retention_d1 | calculated |
| pulled_at | date-time | when I ran the pull (UTC) | |

"Island details" is the API endpoint `GET /islands/{code}`. "Daily metrics" is
`GET /islands/{code}/metrics/day`. The genre leaderboards are `GET /genres/{genre}/rankings`.

A few rules for the calculated columns:
- A ratio is left blank (not 0) if the number it divides by is missing or zero.
- For Epic-made islands, Epic's documentation says favorites and recommendations "are not supported for some
  Epic-made games, so these fields will return 0." I kept the 0 the API returned but left the rate blank, since
  0 there doesn't mean nobody favorited it.

Genre groups:

| genre_group | genres in it |
|---|---|
| Combat & Competitive | Battle Royale, Shooter, Strategy |
| Casual & Party | Party & Mini Games, Music & Rhythm, Deathrun & Platformer, Sports & Racing |
| Adventure, Sim & Social | Adventure & RPG, Simulation & Tycoon, Roleplaying & Social |
| Survival & Horror | Survival, Horror, Roguelike |
| Epic-made (not ranked) | Battle Royale and Reload (Epic's own modes) |

`islands_all.csv` has the same columns minus the two tiers, plus a `problems` column. `daily_history.csv` has one
row per island per day with peak players, plays, unique players, average minutes and both retention numbers.

## Checking the data

The script checks its own work and prints a summary at the end of each run:
- It waits a moment between requests, retries if the API says to slow down, and stops after 400 requests.
- Every failed request is logged with the reason. If more than 5% fail, it prints
  "DATA INTEGRITY FAIL: do not use these results." and doesn't write any CSVs. In my pull, 4 of 152 failed
  (2.6%). All 4 belonged to two islands that were on a leaderboard but couldn't be looked up, and both are listed in `excluded.csv`.
- It looks for duplicates, negative numbers, retention outside 0 to 1, and impossible combinations (like more
  players online at once than played all day). None turned up.
- It flags outliers worth a second look. In my pull those were Battle Royale (3.8 million peak players, far
  above everything else) and GO UP FOR BRAINROTS. That island's peak was 73% of all the players it had that
  day, which is unusually high.
- It compares the all-in-one data request against Epic's single-metric requests for two islands to make sure
  they agree. They did.

## Limitations

- **One day.** The main columns describe a single day (a Sunday in my pull). A weekend, event or update can
  shift an island a lot.
- **Seven days at most.** The API only keeps seven days of history, so this is a snapshot, not a long-term
  trend.
- **Islands with fewer than 5 players are hidden.** Epic shows a blank for these, and I left them out rather
  than guess.
- **Only public islands.** Private or unlisted islands aren't in the API.
- **Not a random sample.** I picked islands by fixed leaderboard ranks, plus two Epic modes. Results describe
  this sample, not all of Fortnite.
- **Retention is rounded** to two decimals by the API, so very small islands often show 0.00.
- **Different timing for picking and measuring.** Islands were picked from the leaderboard at the hour of the
  pull, but their numbers are from the previous full day.
- **No release dates.** The API doesn't say when an island was released, so I couldn't measure island age.

## Where the API didn't match what I expected

Before coding, I read Epic's API documentation. A few things were different from what I planned:
- There's **no release date**, so I couldn't add a "days since release" or "age group" column.
- The `category` field is a **brand name** (like LEGO or TMNT), not a type of game, and it's blank for most
  islands. I used Epic's genres instead.
- **Retention comes back as a share** (0.17), even though Epic's documentation describes it as a number of
  players.
- **Epic's own modes can't be listed.** Only Battle Royale and Reload could be found by name.
- **No login was needed.** Epic's documentation mentions an optional login method, but every request worked
  without one. If that ever changes, the script stops and explains how to set up credentials in a private `.env`
  file, which is never uploaded.

## Extra: product-manager prototypes

These aren't part of the class assignment. They're small prototypes I built to talk through in my interview,
and they only read the CSVs. Each one is labeled as a prototype in its output.
- `report.py` writes `report.md`: the top 10 islands, a retention summary, Epic vs creator islands, and what
  changed since the last pull.
- `anomalies.py` writes `anomalies.md`: days where an island's numbers jumped or dropped compared with its own
  earlier days. It also separates island-specific moves from weekend or Fortnite-wide ones. Seven days is far
  too short for firm conclusions, and the file says so.
- `projection.py` writes `projection.md`: a low-to-high range for next week's peak players, based only on last
  week, with the assumptions written out. It's not a prediction.
- `build_context.py` writes `fortnite_context.md`: a file I can give an AI chatbot with the data and definitions,
  plus 10 test questions with answers taken from the data, to check whether it answers correctly.
