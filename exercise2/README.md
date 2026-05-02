# Music Session Analysis

Large-scale listening session analysis using PySpark and Docker. Processes 19 million play events from the [Last.fm 1K dataset](http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html) to identify the most played songs within the longest listening sessions.

## Main Goal

> The goal was to get the top 10 most played songs across the top 50 longest listening sessions

A session is defined as a continuous sequence of plays by the same user where each song starts within 20 minutes of the previous one.

## How it works

1. **Load** — reads the TSV dataset and parses timestamps
2. **Detect sessions** — uses a LAG window function to compute the gap between consecutive plays per user; flags a new session when the gap exceeds 20 minutes
3. **Assign session IDs** — cumulative sum of the new-session flag gives each session a unique ID per user
4. **Rank sessions** — groups by `(user, session)`, counts tracks, ranks globally by length
5. **Find top songs** — joins back to the original plays, filters to the top 50 sessions, counts song occurrences

## Results

| Rank | Artist | Track | Occurrences |
|------|--------|-------|-------------|
| 1 | Cake | Jolene | 1214 |
| 2 | The Knife | Heartbeats | 868 |
| 3 | Jeff Buckley & Gary Lucas | How Long Will It Take | 726 |
| 4 | Broken Social Scene | Anthems For A Seventeen Year Old Girl | 659 |
| 5 | Elliott Smith | St. Ides Heaven | 646 |
| 6 | The Killers | Bonus Track | 634 |
| 7 | 2Pac | Starin' Through My Rear View | 617 |
| 8 | The Rolling Stones | Beast Of Burden | 613 |
| 9 | Everclear | The Swing | 604 |
| 10 | Kanye West | See You In My Nightmares | 536 |

Full results in [`output/top10_songs.tsv`](output/top10_songs.tsv).

## Running it

**Requirements:** Docker

```bash
# 1. Place the dataset files inside data/
#    Download from: http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html

# 2. Build and run
docker compose up --build

# 3. Results appear in output/top10_songs.tsv
```

## Design decisions

**`rank()` over `row_number()`** — if two sessions tie at position 50, both are included. Dropping one arbitrarily would give a misleading result.

**8 shuffle partitions** — the default of 200 is designed for large clusters. Running on a single node, 8 partitions eliminates unnecessary scheduling overhead without sacrificing correctness.

**`collect()` for output** — the result is 10 rows. Pulling to the driver and writing with standard file I/O produces a single clean TSV rather than Spark's multi-part output directory.

## References

- [Last.fm 1K Dataset](http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html) — dataset source and description
- [`data/README.txt`](data/README.txt) — dataset format and column definitions
- [PySpark Window Functions](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Window.html) — used for LAG and cumulative sum
- [PySpark SQL Functions](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html) — full function reference
- [Docker Compose documentation](https://docs.docker.com/compose/) — volume mounts and service configuration
