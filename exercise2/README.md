# Session Analysis

Processes 19 million play events from the [Last.fm 1K dataset](http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html) using PySpark to find which songs appear most in people's longest listening sessions.

**Main objective**: when someone sits down for a marathon listening session, what are they actually playing?

## How it works

Sessions are defined by gaps in play time, if more than 20 minutes pass between two songs, it's considered a new session. 

The pipeline:

1. Loads and parses the TSV dataset, converting timestamps to proper datetime types
2. Detects session boundaries using a LAG window function per user
3. Assigns session IDs via cumulative sum of the new-session flag
4. Ranks all sessions globally by track count, keeps the top 50
5. Counts song occurrences within those sessions

## Results

| Rank | Artist | Track | Plays |
|------|--------|-------|-------|
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

Docker handles everything — no local Spark or Java setup needed.

```bash
# 1. Place the dataset TSV inside the repo root data/ folder

# 2. From this directory (exercise2/), run:
docker compose up --build

# 3. Results appear in exercise2/output/top10_songs.tsv
```

## A few implementation notes

- **`rank()` instead of `row_number()`** — if two sessions tie at position 50, both are included. Dropping one arbitrarily would skew the song counts.

- **8 shuffle partitions** — Spark defaults to 200, which makes sense for large clusters. On a single machine using less partitions improves efficency.

- **`collect()` for the final write** — the output is 10 rows. Writing from the driver produces one clean file instead of Spark's default multi-part directory.

## Things to improve on with more time

- **Parameterise the session gap and top-N** — the 20-minute threshold and top-50 sessions are hardcoded. Making them CLI arguments would let you explore how sensitive the results are to those choices.
- **Add unit tests** — the session detection logic (LAG + cumsum) is the core of the pipeline and the most likely place for subtle bugs. A small test suite with known inputs and expected outputs would make it much more robust.
- **Write results to Delta Lake** — for a production setting, writing to a TSV is fine for exploration but the output should land in a proper data lake layer so downstream consumers can query it reliably.
- **Explore streaming session detection** — the current approach is batch. For a real-time recommendation system you'd want to detect session boundaries as events arrive, which would require a streaming approach with something like Spark Structured Streaming.

## References

- [Last.fm 1K Dataset](http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html)
- [`data/README.txt`](../data/README.txt) — column definitions and format details
- [PySpark Window Functions](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Window.html)
- [Docker Compose](https://docs.docker.com/compose/)
