# Peak CCU range for the next 7 days (PROTOTYPE, not a prediction)

Based on 2026-11-09 to 2026-11-15 (UTC). Range shown for 2026-11-16 to 2026-11-22.

| Island | Latest day | Low | Typical (median) | High | Range width (% of typical) | Warning |
|---|---|---|---|---|---|---|
| Battle Royale | 3,774,221 | 1,873,334 | 2,347,752 | 6,364,333 | 191.3% |  |
| Reload | 95,810 | 53,033 | 68,593 | 95,810 | 62.4% |  |
| PILLARS | 62,801 | 37,473 | 52,416 | 73,330 | 68.4% |  |
| BOX PVP | 23,935 | 16,362 | 21,421 | 33,010 | 77.7% |  |
| Piece Control 2v2 🎯 | 25,040 | 12,628 | 17,801 | 31,442 | 105.7% |  |
| GO UP FOR BRAINROTS | 215,575 | 15,679 | 16,638 | 258,227 | 1457.8% | LEVEL SHIFT: last 2 days are 14.3x the first half of the week; range is not meaningful |
| Bed Wars | 10,038 | 5,272 | 8,315 | 10,038 | 57.3% |  |
| CRAZY RED VS BLUE 🔴🔵 | 8,978 | 4,285 | 6,134 | 9,272 | 81.3% |  |
| Break The Egg | 6,285 | 119 | 199 | 6,285 | 3098.5% | LEVEL SHIFT: last 2 days are 31.1x the first half of the week; range is not meaningful |
| 2233 ⭐ HARD PARKOUR DEATHRUN باركور | 8,441 | 57 | 71 | 8,441 | 11808.5% | LEVEL SHIFT: last 2 days are 37.3x the first half of the week; range is not meaningful |

A LEVEL SHIFT warning means the median of the last 2 days is at least 3x (or at most 1/3) the median of the first half of the week. The island changed during the week (breakout, feature, update), so last week's range says little about next week.

## Assumptions (read before using)
- Next week behaves like the last 7 days: no new season, patch, live event, featured placement, creator update or outage that the last 7 days did not already contain.
- Each day's peak is drawn from the same range as last week; weekday/weekend patterns are not modelled (7 days contain only one weekend).
- If last week contained a one-off spike (for example a live event), the 'high' end includes it and is probably too optimistic for a normal week.
- Nulls (Epic hides values when fewer than 5 unique players) are left out, never treated as 0.
- The range covers only what was observed. Real values can and will fall outside it.

_How to use in a PM conversation: 'If nothing changes, we would expect daily peak CCU somewhere between low and high. A day outside that range is a signal to investigate, not a forecast miss.'_