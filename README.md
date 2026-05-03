# Music-Behaviour-Analytics

A listening behaviour analysis at scale using the [Last.fm 1K dataset](http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html), which has 19 million play events from 1,000 users collected between 2005 and 2009.

Questions required for this project:

- Which songs appear most in people's longest listening sessions?
- Can we predict how often a power user will listen in the coming months?

## Exercise 2 — Session analysis (PySpark + Docker)

Processes the full dataset to find the top 10 most-played songs across the 50 longest listening sessions. Runs in a Docker container. Local Spark setup not needed.

→ [How it works and results](exercise2/README.md)
→ [Top 10 songs](exercise2/output/top10_songs.tsv)

## Exercise 3 — Behaviour forecast (pandas + Prophet)

Identifies the most active user in the dataset and forecasts their weekly session count 3 months out using Meta's Prophet.

→ [How it works and results](exercise3/README.md)  
→ [Forecast data](exercise3/output/forecast.tsv)

## Dataset

[Last.fm Dataset — 1K users](http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html) by Òscar Celma. Not included here due to size — download and place the TSV at `data/` before running.
