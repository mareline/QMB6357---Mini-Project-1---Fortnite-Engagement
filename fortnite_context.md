# Fortnite island engagement: context file for LLM questions (PROTOTYPE)

You are answering questions about a small sample of Fortnite islands. Use ONLY the data and definitions in this file. If the file does not contain the answer, say so. Never estimate a missing value.

## Source and timing
- Source: Epic Games' public Fortnite Data API, `https://api.fortnite.com/ecosystem/v1` (spec v1.1.0).
- Pulled at: 2026-11-16T23:35:11Z. All '24h' metrics are for the full UTC day **2026-11-15**.
- Sample: 67 islands pulled, 56 with complete data (the table below). The sample is 5 islands from each of Epic's 13 discovery genres (ranks 1, 10, 50, 150 and 400 in an hourly genre ranking) plus 2 Epic-made modes (Battle Royale, Reload). It is NOT all of Fortnite and NOT a random sample.

## Metric definitions (Epic's wording, plus what the data actually looks like)
| Column | Definition | Unit / format | Endpoint |
|---|---|---|---|
| peak_ccu_24h | Peak number of concurrent players playing the island | players | peakCCU |
| plays_24h | Times players started the island; repeat starts by the same player each count | plays | plays |
| unique_players_24h | Number of unique players playing the island | players | uniquePlayers |
| minutes_played_24h | Total minutes players spent on the island | minutes | minutesPlayed |
| avg_minutes_per_player | Average minutes per player | minutes | averageMinutesPerPlayer |
| favorites | Times the island was added to a player's favorites | count | favorites |
| recommendations | Times the island was recommended by a player | count | recommendations |
| retention_d1 | Spec: 'players retained from the previous day' | 0-1 fraction, 2 decimals | retention (d1) |
| retention_d7 | Spec: 'players retained from the previous 7 days' | 0-1 fraction, 2 decimals | retention (d7) |
| plays_per_player | plays_24h / unique_players_24h (derived) | ratio | - |
| favorite_rate | favorites / unique_players_24h (derived) | ratio | - |
| recommend_rate | recommendations / unique_players_24h (derived) | ratio | - |
| ccu_tier | Low/Medium/High terciles of peak_ccu_24h within this sample | text | - |
| retention_tier | Low/Medium/High terciles of retention_d1 within this sample | text | - |
| genre / genre_group | Epic discovery genre of the ranking the island came from / 4 broader groups | text | /genres/{slug}/rankings |
| epic_made | Yes if the island's creatorCode is 'epic' | Yes/No | /islands/{code} |

Metric columns come from `GET /islands/{code}/metrics/day` (one daily bucket per UTC day). Island title, creator, tags and createdIn come from `GET /islands/{code}`.

## Known limits
- Only 7 days of history exist in the API; this is a snapshot, not a long-term trend.
- Epic returns **null** when an island had fewer than 5 unique players in the interval. Nulls are excluded from the clean table, never replaced by 0.
- Only public, discoverable islands are in the API.
- Favorites and recommendations can be 0 for some Epic-made modes because Epic does not track them there.
- Retention is a 0-1 fraction rounded to 2 decimals, although Epic's spec calls it a 'number of players'.
- The API has no release date, so island age cannot be computed.
- Only 2 Epic-made islands are in the sample; Epic vs creator comparisons are not representative.

## Data: clean islands (56 rows, metrics day 2026-11-15)
```csv
island_code,title,creator,epic_made,genre,genre_group,peak_ccu_24h,plays_24h,unique_players_24h,avg_minutes_per_player,favorites,recommendations,retention_d1,retention_d7,ccu_tier,retention_tier
8212-2620-5211,BOSS SURVIVAL ULTIMATE BATTLE,justmapping,No,Survival,Survival & Horror,290,10389,8342,25.35,271,42,0.16,0.06,Medium,Medium
5351-7221-3223,Zombie Raiders: Loot & Survive,snowfallgames,No,Survival,Survival & Horror,26,568,473,33.0,36,1,0.08,0.02,Low,Low
1534-0561-0768,ZOMBIE HOSPITAL,ultraeliassj_yt,No,Survival,Survival & Horror,16,280,264,14.22,10,0,0.08,0.0,Low,Low
7048-8422-2298,Bed Wars,goodgamers,No,Strategy,Combat & Competitive,10038,413152,205155,44.43,1106,300,0.34,0.16,High,High
4164-3090-6037,Bed Wars Klombos [PvP BedWars],minigames,No,Strategy,Combat & Competitive,365,11869,7107,40.22,85,13,0.26,0.09,Medium,Medium
1666-5448-0514,2026 NEW YEAR ESCAPE ROOM,bqv,No,Strategy,Combat & Competitive,43,793,784,33.11,38,7,0.04,0.02,Low,Low
6807-6809-1375,Pizza Simulator,pamsha,No,Strategy,Combat & Competitive,7,85,70,15.3,12,2,0.22,0.0,Low,Medium
2678-5257-1845,SUPER RAMP,pixelstudio,No,Sports & Racing,Casual & Party,2590,132035,111034,17.08,1881,1012,0.11,0.02,High,Low
2855-9139-7238,MONZA RACE TRACK 🇮🇹 FOA,luxfortnite,No,Sports & Racing,Casual & Party,46,1148,960,17.16,45,3,0.11,0.03,Low,Low
1796-8315-5749,🚗 RUSHPATH CITY CAR DRIVE 🚗,justmapping,No,Sports & Racing,Casual & Party,15,195,142,30.18,4,3,0.28,0.09,Low,High
7875-7934-3852,GO UP FOR BRAINROTS,ferins,No,Simulation & Tycoon,"Adventure, Sim & Social",215575,1606771,295347,105.66,1512,1283,0.82,0.65,High,High
8440-2283-1538,Break The Egg,smuti,No,Simulation & Tycoon,"Adventure, Sim & Social",6285,135347,84257,54.09,4063,1056,0.23,0.21,High,Medium
8487-6187-7872,Dig Out of School 🏫,muloky,No,Simulation & Tycoon,"Adventure, Sim & Social",405,23004,20166,16.94,746,124,0.04,0.01,Medium,Low
0226-0902-7042,SCHOOL TYCOON,detooxgod,No,Simulation & Tycoon,"Adventure, Sim & Social",53,1724,1376,25.04,79,10,0.1,0.01,Medium,Low
5838-0027-6903,FIGHT BRAINROT FOR BRAINROTS TYCOON,svet,No,Simulation & Tycoon,"Adventure, Sim & Social",2,9,9,18.89,1,0,0.0,0.0,Low,Low
0148-0322-5437,Piece Control 2v2 🎯,bullseye,No,Shooter,Combat & Competitive,25040,2313115,1043230,21.97,4953,1413,0.36,0.22,High,High
2898-7886-8847,CRAZY RED VS BLUE 🔴🔵,rvb,No,Shooter,Combat & Competitive,8978,381045,260675,30.66,1378,1150,0.34,0.15,High,High
1650-4346-6758,WILD SNIPER ONE SHOT 🎯,rezentlyfn,No,Shooter,Combat & Competitive,1416,67226,49870,24.03,581,158,0.26,0.08,High,Medium
5686-1739-4834,"🎯Practice Warm-Up (Aim, Edit, Piece)",teadoh,No,Shooter,Combat & Competitive,191,9128,6570,21.38,199,19,0.26,0.11,Medium,Medium
0792-2608-4018,1v1 Build Fights! (TypicalGamer),jogo,No,Shooter,Combat & Competitive,55,4107,2151,17.93,60,11,0.22,0.1,Medium,Medium
9909-6421-7669,CASH CITY,johnnyblueprint,No,Roleplaying & Social,"Adventure, Sim & Social",3466,110399,72396,44.68,750,183,0.34,0.14,High,High
4220-9404-7987,Sprite Garden,epicgames,No,Roleplaying & Social,"Adventure, Sim & Social",878,80415,62837,10.96,1293,382,0.16,0.09,High,Medium
3369-4671-4228,✈️ Airport Drive 🚀,chocowaka,No,Roleplaying & Social,"Adventure, Sim & Social",227,6668,4247,44.92,41,18,0.41,0.21,Medium,High
7465-5762-7170,CALIFORTIA HOOD,justfortnite,No,Roleplaying & Social,"Adventure, Sim & Social",45,980,719,38.35,47,6,0.21,0.08,Low,Medium
7057-0891-8258,Brookhaven fortnite🛑new Update !,manisy,No,Roleplaying & Social,"Adventure, Sim & Social",5,85,67,9.13,4,1,0.0,0.0,Low,Low
9214-0706-7537,ESCAPE FROM HOSPITAL [ROGUELIKE],adamthecreator,No,Roguelike,Survival & Horror,4472,30250,26670,29.75,1235,86,0.14,0.04,High,Medium
8105-9005-4478,HEIST ESCAPE ROGUELIKE PAYDAY EXPERIENCE,ocwg,No,Roguelike,Survival & Horror,382,10171,7508,51.23,179,33,0.27,0.1,Medium,High
2028-6930-4527,STRANGER THINGS ESCAPE 3 [ROGUELIKE],hedwig,No,Roguelike,Survival & Horror,20,456,345,36.7,30,2,0.25,0.09,Low,Medium
7786-0958-2481,PILLARS,hive,No,Party & Mini Games,Casual & Party,62801,2080106,1420031,37.84,8503,3622,0.36,0.2,High,High
5581-8600-6431,GENESIS SQUID GAME,genesisstudios,No,Party & Mini Games,Casual & Party,1938,168293,79751,24.64,928,212,0.22,0.09,High,Medium
8742-0736-8164,DON'T PRESS THE BUTTON 140+ MINIGAMES 👑,don-frederik-bos,No,Party & Mini Games,Casual & Party,341,11309,8572,34.33,144,63,0.27,0.09,Medium,High
0610-5874-3886,😹 FALL GUYS BACKROOMS - NEXTBOT 👽,dropstudio,No,Party & Mini Games,Casual & Party,52,2057,1715,19.26,25,7,0.18,0.05,Medium,Medium
7440-1316-6284,ماب تسونامي,s6o,No,Party & Mini Games,Casual & Party,11,129,109,19.72,4,2,0.15,0.05,Low,Medium
5494-2125-5108,GUESS the MEME SONG,sonoq,No,Music & Rhythm,Casual & Party,435,26947,22317,17.17,524,81,0.12,0.02,Medium,Medium
6253-2742-8438,TRAVIS SCOTT ASTRONOMICAL LIVE EVENT 🌌,4getable,No,Music & Rhythm,Casual & Party,103,5795,5383,13.02,357,52,0.04,0.01,Medium,Low
1255-8147-5899,Guess The Song (Music Blocks) 20+ Songs,zerok,No,Music & Rhythm,Casual & Party,6,141,122,12.14,13,3,0.03,0.01,Low,Low
8462-7059-9097,Sleep and Chill v2💤,kj3000,No,Music & Rhythm,Casual & Party,3,8,8,6.25,1,0,0.33,0.0,Low,High
8447-6753-2253,Backrooms: Remastered [HORROR],redlinestudios,No,Horror,Survival & Horror,440,22214,18092,19.46,915,71,0.04,0.01,Medium,Low
7740-2617-6370,RAINBOW FRIENDS,cheerz,No,Horror,Survival & Horror,460,40016,35657,9.82,1531,107,0.07,0.01,Medium,Low
2633-7144-2490,BACKROOMS: LEVELS [HORROR],pequ,No,Horror,Survival & Horror,110,4218,3476,26.38,157,59,0.1,0.02,Medium,Low
2478-1176-5428,Halloween Shift [HORROR],akina,No,Horror,Survival & Horror,17,353,284,24.63,66,6,0.02,0.0,Low,Low
8894-6427-7270,🎡Teletubbies Park- Rank Horror Gun Game,gerox,No,Horror,Survival & Horror,5,20,19,9.21,1,0,0.0,0.0,Low,Low
5389-9648-9460,2233 ⭐ HARD PARKOUR DEATHRUN باركور,zenasd,No,Deathrun & Platformer,Casual & Party,8441,68244,63229,19.07,1388,388,0.14,0.02,High,Medium
1798-2026-9632,ESCAPE BARRY 2 FALL GUYS [Obby],miniarcades,No,Deathrun & Platformer,Casual & Party,506,30607,26650,16.28,308,80,0.07,0.01,High,Low
9298-0844-6419,+1 BOTTLE FLIP ESCAPE 🚀,patamayv,No,Deathrun & Platformer,Casual & Party,129,4556,3993,19.29,231,41,0.13,0.01,Medium,Medium
5497-6332-8508,DEATHRUN SATAN REMAKE TEAM CROUTON MICH,mickel,No,Deathrun & Platformer,Casual & Party,24,419,377,22.41,6,0,0.15,0.02,Low,Medium
5784-7733-4505,🌼iNSANE 350+ DRIFT PAKOUR🌼,shaggypotato,No,Deathrun & Platformer,Casual & Party,5,28,27,14.48,0,0,0.1,0.0,Low,Low
2515-6266-7600,BOX PVP,hive,No,Battle Royale,Combat & Competitive,23935,1408532,920797,22.3,4176,2577,0.32,0.19,High,High
6013-7804-4824,Desert Zone Wars🌵,pandvil,No,Battle Royale,Combat & Competitive,2192,79569,59762,29.82,596,102,0.16,0.08,High,Medium
7413-3133-3758,Endless Zone Wars,pwr,No,Battle Royale,Combat & Competitive,329,13392,9828,24.88,150,15,0.28,0.1,Medium,High
0797-1278-3702,BOX FIGHTS OR ZONE WARS,nvq,No,Battle Royale,Combat & Competitive,84,2323,1755,25.79,23,5,0.22,0.04,Medium,Medium
8123-7265-8270,CYPRUS ZONE WARS,piella,No,Battle Royale,Combat & Competitive,11,49,47,29.72,2,0,0.3,0.04,Low,High
1679-1641-4012,KICK FOOD FOR ANIMALS,gako,No,Adventure & RPG,"Adventure, Sim & Social",3953,55383,39155,43.86,3028,665,0.29,0.04,High,High
2101-2805-5748,Blox Fruits (Sea 1),savageboi,No,Adventure & RPG,"Adventure, Sim & Social",15,469,429,9.07,28,2,0.01,0.0,Low,Low
experience_br,Battle Royale,epic,Yes,,Epic-made (not ranked),3774221,229408324,28751731,94.71,240172,264587,0.71,0.57,High,High
experience_reload,Reload,epic,Yes,,Epic-made (not ranked),95810,8937948,2336858,37.01,26799,13489,0.41,0.26,High,High
```

## Data: excluded islands and why
```csv
island_code,title,genre,reason
9860-2610-1282,LUCKY BLOCK SKYBLOCK [ADVENTURE],Survival,retention_d7: null from API
6922-2142-3252,Demon Hunter Rush 🦖👹⚔️,Survival,peak_ccu_24h: null from API; plays_24h: null from API; unique_players_24h: null from API; minutes_played_24h: null from API; avg_minutes_per_player: null from API; favorites: null from API; recommendations: null from API; retention_d1: null from API; retention_d7: null from API
7595-3862-7607,,Strategy,metadata call failed; metrics call failed
4341-3378-7617,CLIMB THE HILL,Sports & Racing,retention_d1: null from API; retention_d7: null from API
0876-1035-8659,TMNT - CAR DRIVER,Sports & Racing,peak_ccu_24h: null from API; plays_24h: null from API; unique_players_24h: null from API; minutes_played_24h: null from API; avg_minutes_per_player: null from API; favorites: null from API; recommendations: null from API; retention_d1: null from API; retention_d7: null from API
3869-0322-0495,Z-MOTEL ROGUELIKE,Roguelike,retention_d1: null from API; retention_d7: null from API
1269-8523-7073,Backrooms Runners [Roguelike],Roguelike,peak_ccu_24h: null from API; plays_24h: null from API; unique_players_24h: null from API; minutes_played_24h: null from API; avg_minutes_per_player: null from API; favorites: null from API; recommendations: null from API; retention_d1: null from API; retention_d7: null from API
0782-2430-3701,桜の花,Music & Rhythm,peak_ccu_24h: null from API; plays_24h: null from API; unique_players_24h: null from API; minutes_played_24h: null from API; avg_minutes_per_player: null from API; favorites: null from API; recommendations: null from API; retention_d1: null from API; retention_d7: null from API
0567-6683-5899,GALACTUS EVENT - THE DEVOURER OF WORLDS,Adventure & RPG,retention_d7: null from API
2049-8381-8507,Clean The Bugs,Adventure & RPG,recommendations: null from API; retention_d7: null from API
4809-6981-3892,,Adventure & RPG,metadata call failed; metrics call failed
```

## Data: daily history (7 UTC days) for the 10 largest islands by peak CCU
```csv
island_code,title,epic_made,date,peak_ccu,plays,unique_players,avg_minutes_per_player,retention_d1,retention_d7
0148-0322-5437,Piece Control 2v2 🎯,No,2026-11-09,12628,1131789,547897,20.28,0.3,0.22
0148-0322-5437,Piece Control 2v2 🎯,No,2026-11-10,16043,1254936,621716,19.65,0.22,0.17
0148-0322-5437,Piece Control 2v2 🎯,No,2026-11-11,17801,1629255,782567,20.52,0.3,0.18
0148-0322-5437,Piece Control 2v2 🎯,No,2026-11-12,13747,1178826,554207,19.95,0.33,0.21
0148-0322-5437,Piece Control 2v2 🎯,No,2026-11-13,22351,1655633,776753,20.65,0.24,0.17
0148-0322-5437,Piece Control 2v2 🎯,No,2026-11-14,31442,2329050,1069699,21.96,0.33,0.19
0148-0322-5437,Piece Control 2v2 🎯,No,2026-11-15,25040,2313115,1043230,21.97,0.36,0.22
2515-6266-7600,BOX PVP,No,2026-11-09,16362,832140,582503,20.51,0.28,0.19
2515-6266-7600,BOX PVP,No,2026-11-10,20452,945900,671676,20.89,0.21,0.14
2515-6266-7600,BOX PVP,No,2026-11-11,21421,1166958,797715,21.48,0.28,0.15
2515-6266-7600,BOX PVP,No,2026-11-12,17493,832667,578851,20.71,0.3,0.17
2515-6266-7600,BOX PVP,No,2026-11-13,26889,1201163,811862,22.03,0.22,0.14
2515-6266-7600,BOX PVP,No,2026-11-14,33010,1539754,977541,22.68,0.31,0.18
2515-6266-7600,BOX PVP,No,2026-11-15,23935,1408532,920797,22.3,0.32,0.19
2898-7886-8847,CRAZY RED VS BLUE 🔴🔵,No,2026-11-09,5233,226679,159319,28.5,0.28,0.15
2898-7886-8847,CRAZY RED VS BLUE 🔴🔵,No,2026-11-10,5540,227831,158374,28.42,0.2,0.11
2898-7886-8847,CRAZY RED VS BLUE 🔴🔵,No,2026-11-11,6134,256947,176717,29.22,0.29,0.12
2898-7886-8847,CRAZY RED VS BLUE 🔴🔵,No,2026-11-12,4285,183332,125006,27.7,0.31,0.14
2898-7886-8847,CRAZY RED VS BLUE 🔴🔵,No,2026-11-13,6290,259642,177904,28.95,0.22,0.11
2898-7886-8847,CRAZY RED VS BLUE 🔴🔵,No,2026-11-14,9272,446535,301845,29.5,0.32,0.13
2898-7886-8847,CRAZY RED VS BLUE 🔴🔵,No,2026-11-15,8978,381045,260675,30.66,0.34,0.15
5389-9648-9460,2233 ⭐ HARD PARKOUR DEATHRUN باركور,No,2026-11-09,114,1504,1385,30.5,0.1,
5389-9648-9460,2233 ⭐ HARD PARKOUR DEATHRUN باركور,No,2026-11-10,145,2119,1898,29.97,0.12,
5389-9648-9460,2233 ⭐ HARD PARKOUR DEATHRUN باركور,No,2026-11-11,71,1632,1401,38.78,0.13,
5389-9648-9460,2233 ⭐ HARD PARKOUR DEATHRUN باركور,No,2026-11-12,57,932,847,35.21,0.12,
5389-9648-9460,2233 ⭐ HARD PARKOUR DEATHRUN باركور,No,2026-11-13,61,1029,936,35.31,0.09,
5389-9648-9460,2233 ⭐ HARD PARKOUR DEATHRUN باركور,No,2026-11-14,67,1348,1206,35.15,0.16,
5389-9648-9460,2233 ⭐ HARD PARKOUR DEATHRUN باركور,No,2026-11-15,8441,68244,63229,19.07,0.14,0.02
7048-8422-2298,Bed Wars,No,2026-11-09,6334,241529,126681,39.53,0.31,0.17
7048-8422-2298,Bed Wars,No,2026-11-10,6805,242118,132074,38.73,0.21,0.14
7048-8422-2298,Bed Wars,No,2026-11-11,8315,305559,155263,41.21,0.31,0.15
7048-8422-2298,Bed Wars,No,2026-11-12,5272,197470,105239,39.51,0.33,0.17
7048-8422-2298,Bed Wars,No,2026-11-13,8784,278279,143951,40.82,0.24,0.14
7048-8422-2298,Bed Wars,No,2026-11-14,9572,375963,197327,42.5,0.34,0.16
7048-8422-2298,Bed Wars,No,2026-11-15,10038,413152,205155,44.43,0.34,0.16
7786-0958-2481,PILLARS,No,2026-11-09,42165,1253709,886857,34.84,0.33,0.21
7786-0958-2481,PILLARS,No,2026-11-10,48914,1392558,960125,35.27,0.24,0.17
7786-0958-2481,PILLARS,No,2026-11-11,52416,1703419,1129914,36.82,0.33,0.18
7786-0958-2481,PILLARS,No,2026-11-12,37473,1086874,784687,34.98,0.35,0.2
7786-0958-2481,PILLARS,No,2026-11-13,59480,1553310,1059649,36.1,0.25,0.16
7786-0958-2481,PILLARS,No,2026-11-14,73330,2141589,1429467,37.06,0.34,0.19
7786-0958-2481,PILLARS,No,2026-11-15,62801,2080106,1420031,37.84,0.36,0.2
7875-7934-3852,GO UP FOR BRAINROTS,No,2026-11-09,16638,784748,129004,135.91,0.56,0.53
7875-7934-3852,GO UP FOR BRAINROTS,No,2026-11-10,16568,828903,124770,140.39,0.38,0.42
7875-7934-3852,GO UP FOR BRAINROTS,No,2026-11-11,16349,885181,129443,138.78,0.63,0.48
7875-7934-3852,GO UP FOR BRAINROTS,No,2026-11-12,15679,848333,129092,128.68,0.64,0.53
7875-7934-3852,GO UP FOR BRAINROTS,No,2026-11-13,18610,1098521,151679,141.47,0.6,0.51
7875-7934-3852,GO UP FOR BRAINROTS,No,2026-11-14,258227,1894079,344450,105.45,0.68,0.54
7875-7934-3852,GO UP FOR BRAINROTS,No,2026-11-15,215575,1606771,295347,105.66,0.82,0.65
8440-2283-1538,Break The Egg,No,2026-11-09,199,4613,2643,50.65,0.34,0.12
8440-2283-1538,Break The Egg,No,2026-11-10,178,4185,2506,51.53,0.25,0.08
8440-2283-1538,Break The Egg,No,2026-11-11,186,4225,2594,51.47,0.36,0.08
8440-2283-1538,Break The Egg,No,2026-11-12,119,3863,2498,42.03,0.37,0.11
8440-2283-1538,Break The Egg,No,2026-11-13,4842,82131,59896,39.24,0.31,0.11
8440-2283-1538,Break The Egg,No,2026-11-14,5295,156942,102354,45.84,0.52,0.26
8440-2283-1538,Break The Egg,No,2026-11-15,6285,135347,84257,54.09,0.23,0.21
experience_br,Battle Royale,Yes,2026-11-09,2371430,179857872,24820424,88.06,0.71,0.65
experience_br,Battle Royale,Yes,2026-11-10,2337500,169171183,24424753,83.65,0.58,0.54
experience_br,Battle Royale,Yes,2026-11-11,2347752,184181659,25536936,86.63,0.65,0.53
experience_br,Battle Royale,Yes,2026-11-12,1873334,138229422,22475668,74.03,0.67,0.55
experience_br,Battle Royale,Yes,2026-11-13,2199025,157971412,24417146,77.59,0.57,0.48
experience_br,Battle Royale,Yes,2026-11-14,6364333,247124945,29592377,101.51,0.65,0.51
experience_br,Battle Royale,Yes,2026-11-15,3774221,229408324,28751731,94.71,0.71,0.57
experience_reload,Reload,Yes,2026-11-09,53033,4842347,1448089,31.62,0.36,0.19
experience_reload,Reload,Yes,2026-11-10,57226,4787911,1444859,32.62,0.27,0.17
experience_reload,Reload,Yes,2026-11-11,68593,6049321,1702199,34.0,0.36,0.19
experience_reload,Reload,Yes,2026-11-12,54106,3750256,1195264,35.75,0.39,0.23
experience_reload,Reload,Yes,2026-11-13,74389,5943348,1716918,33.86,0.3,0.2
experience_reload,Reload,Yes,2026-11-14,86068,8395459,2261070,35.74,0.4,0.23
experience_reload,Reload,Yes,2026-11-15,95810,8937948,2336858,37.01,0.41,0.26
```

## Test questions
1. Which island had the highest peak concurrent players on 2026-11-15 (UTC), and what was the value?
2. How many islands are in the clean dataset, and how many pulled islands were excluded?
3. What is the median D1 retention across the clean islands? Give it as a percentage.
4. Which genre_group has the most islands in the clean dataset, and how many?
5. What was Reload's average minutes per player on the metrics day?
6. Among creator-made (not Epic) islands, which had the highest D1 retention?
7. What peak_ccu_24h values separate the Low, Medium and High ccu_tier groups?
8. On which day in the 7-day history did Battle Royale have its highest peak CCU, and what was it?
9. What was the D7 retention of LUCKY BLOCK SKYBLOCK [ADVENTURE] (9860-2610-1282)?
10. How many days ago was Battle Royale released?

## Answer key (remove this section before giving the file to the LLM)
1. Battle Royale (experience_br) with 3,774,221.
2. 56 clean; 11 excluded (of 67 pulled).
3. 17.0% (retention_d1 median = 0.170).
4. Casual & Party with 17 islands.
5. 37.01 minutes.
6. GO UP FOR BRAINROTS (7875-7934-3852) at 0.82.
7. Low <= 48.0; Medium > 48.0 and <= 490.7; High > 490.7.
8. 2026-11-14 with 6,364,333.
9. Not available: the API returned null for retention_d7 on that day (Epic returns null when there is too little data, e.g. fewer than 5 unique players). It must not be guessed or treated as 0.
10. The data cannot answer this: the Fortnite Data API does not provide a release date.