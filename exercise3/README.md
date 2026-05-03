# Session Forecast

Time series forecast of weekly listening sessions for the most active user in the [Last.fm 1K dataset](http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html), using pandas and Prophet.

## Goal

> Identify the user with the most listening sessions and forecast their weekly session count for the next 3 months.

## Approach

### 1. Session detection (pandas)

The dataset has 19 million rows across 1,000 users. Exercise 2 handled this at scale with PySpark. Here, since we only need per-user aggregates, pandas is sufficient and far simpler — no Spark overhead for what amounts to a few thousand rows per user.

Session boundaries follow the same rule as Exercise 2: a new session starts whenever the gap between two consecutive plays exceeds 20 minutes, or when it is the first play of the day.

```python
df["prev_ts"] = df.groupby("userid")["ts"].shift(1)
df["gap_min"] = (df["ts"] - df["prev_ts"]).dt.total_seconds() / 60
df["is_new_session"] = (df["prev_ts"].isna()) | (df["gap_min"] > 20)
df["session_id"] = df.groupby("userid")["is_new_session"].cumsum()
```

### 2. Top user

Counting unique sessions per user yields **user_000833** as the most active listener, with **6,897 sessions** across the full dataset (2005–2009).

### 3. Time series construction

Sessions are aggregated by week — weekly granularity smooths out daily noise and fills gaps naturally, which improves model fit. The result is a `(ds, y)` dataframe ready for Prophet.

### 4. Forecasting with Prophet

[Prophet](https://facebook.github.io/prophet/) is Meta's open-source forecasting library, designed for time series with trend changes and missing data. It fits a decomposable model (trend + seasonality + holidays) and produces uncertainty intervals out of the box.

Configuration choices:
- `weekly_seasonality=True` — the user's listening behaviour varies across days of the week
- `periods=13, freq="W"` — 13 weeks ≈ 3 months, as required by the problem statement

```python
model = Prophet(weekly_seasonality=True)
model.fit(weekly_df)
future = model.make_future_dataframe(periods=13, freq="W")
forecast_df = model.predict(future)
```

## Results

The model captures a clear upward trend in user_000833's activity from early 2005 to late 2008, followed by a plateau. The 3-month forecast projects roughly **35–45 sessions per week**, consistent with the user's recent baseline.

![Forecast plot](output/forecast_plot.png)

Full forecast in [`output/forecast.tsv`](output/forecast.tsv) — columns: `ds`, `yhat`, `yhat_lower`, `yhat_upper`.

## Running it

```bash
pip install -r requirements.txt
python forecast.py
# outputs: output/forecast.tsv, output/forecast_plot.png
```

## References

- [Prophet documentation](https://facebook.github.io/prophet/docs/quick_start.html)
- [Last.fm 1K Dataset](http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html)
- [`../exercise2/data/README.txt`](../exercise2/data/README.txt) — dataset format and column definitions
