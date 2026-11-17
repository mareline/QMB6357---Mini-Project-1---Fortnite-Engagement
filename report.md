# Fortnite island engagement report (PROTOTYPE)

- Pull: `2026-11-16T23:35:11Z` (snapshot `20261116T233511Z`)
- Metrics day: **2026-11-15 (UTC)**. Every '24h' number covers that one day.
- Islands in the clean dataset: **56** (a sample, not all of Fortnite; see README for how they were chosen).

## 1. Top 10 islands by peak concurrent players
| # | Island | Epic-made | Genre | Peak CCU | Unique players | D1 retention | Avg min/player |
|---|---|---|---|---|---|---|---|
| 1 | Battle Royale | Yes | (not ranked) | 3,774,221 | 28,751,731 | 71% | 94.7 |
| 2 | GO UP FOR BRAINROTS | No | Simulation & Tycoon | 215,575 | 295,347 | 82% | 105.7 |
| 3 | Reload | Yes | (not ranked) | 95,810 | 2,336,858 | 41% | 37.0 |
| 4 | PILLARS | No | Party & Mini Games | 62,801 | 1,420,031 | 36% | 37.8 |
| 5 | Piece Control 2v2 🎯 | No | Shooter | 25,040 | 1,043,230 | 36% | 22.0 |
| 6 | BOX PVP | No | Battle Royale | 23,935 | 920,797 | 32% | 22.3 |
| 7 | Bed Wars | No | Strategy | 10,038 | 205,155 | 34% | 44.4 |
| 8 | CRAZY RED VS BLUE 🔴🔵 | No | Shooter | 8,978 | 260,675 | 34% | 30.7 |
| 9 | 2233 ⭐ HARD PARKOUR DEATHRUN باركور | No | Deathrun & Platformer | 8,441 | 63,229 | 14% | 19.1 |
| 10 | Break The Egg | No | Simulation & Tycoon | 6,285 | 84,257 | 23% | 54.1 |

## 2. Retention summary (share of players who came back)
| metric | count | mean | min | 25% | median | 75% | max |
|---|---|---|---|---|---|---|---|
| retention_d1 | 56 | 0.202 | 0.0 | 0.095 | 0.17 | 0.28 | 0.82 |
| retention_d7 | 56 | 0.084 | 0.0 | 0.01 | 0.04 | 0.1 | 0.65 |

Epic's spec defines D1 as players 'retained from the previous day' and D7 as players 'retained from the previous 7 days'. The API returns both as 0-1 fractions rounded to 2 decimals (the spec calls them a 'number of players'), so read 0.17 as 17%.

## 3. Epic-made vs creator-made islands
| epic_made | islands | median_peak_ccu | median_d1 | median_d7 | median_avg_minutes | median_plays_per_player |
|---|---|---|---|---|---|---|
| No | 54 | 209.0 | 0.16 | 0.04 | 23.22 | 1.244 |
| Yes | 2 | 1935015.5 | 0.56 | 0.415 | 65.86 | 5.902 |

**Caution:** only 2 Epic-made island(s) are in the sample, and creator islands were picked from several ranks per genre (including small islands). Medians here describe this sample only; they are not a fair Epic-vs-creator benchmark.

## 4. Changes since the previous pull
Previous pull: `2026-11-16T23:29:09Z` (metrics day 2026-11-15).

Both pulls cover the **same metrics day**, so any difference below is a data revision or a different island sample, not a change in player behaviour.

- Islands in both pulls: 56; new this pull: 0; no longer in clean set: 0

Biggest peak-CCU moves among islands in both pulls:

| Island | Peak CCU before | Peak CCU now | Change % | D1 change (pts) |
|---|---|---|---|---|
| Piece Control 2v2 🎯 | 25,040 | 25,040 | 0.0 | 0.0 |
| SCHOOL TYCOON | 53 | 53 | 0.0 | 0.0 |
| 😹 FALL GUYS BACKROOMS - NEXTBOT 👽 | 52 | 52 | 0.0 | 0.0 |
| 1v1 Build Fights! (TypicalGamer) | 55 | 55 | 0.0 | 0.0 |
| BOX FIGHTS OR ZONE WARS | 84 | 84 | 0.0 | 0.0 |
| Guess The Song (Music Blocks) 20+ Songs | 6 | 6 | 0.0 | 0.0 |
| ZOMBIE HOSPITAL | 16 | 16 | 0.0 | 0.0 |
| WILD SNIPER ONE SHOT 🎯 | 1,416 | 1,416 | 0.0 | 0.0 |
| 2026 NEW YEAR ESCAPE ROOM | 43 | 43 | 0.0 | 0.0 |
| KICK FOOD FOR ANIMALS | 3,953 | 3,953 | 0.0 | 0.0 |

---
_Prototype: numbers come straight from islands_clean.csv. No forecasting, no causal claims._