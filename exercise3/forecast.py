import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

DATA_PATH = "../exercise2/data/userid-timestamp-artid-artname-traid-traname.tsv"


def load_and_build_sessions(path):
    df = pd.read_csv(path, sep="\t", header=None,
                     names=["userid", "timestamp", "artistid", "artist_name", "trackid", "track_name"],
                     on_bad_lines="skip")
    df["ts"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.dropna(subset=["userid", "ts", "track_name"])
    df = df.sort_values(["userid", "ts"])
    df["prev_ts"] = df.groupby("userid")["ts"].shift(1)
    df["gap_min"] = (df["ts"] - df["prev_ts"]).dt.total_seconds() / 60
    df["is_new_session"] = (df["prev_ts"].isna()) | (df["gap_min"] > 20)
    df["session_id"] = df.groupby("userid")["is_new_session"].cumsum()
    return df


def get_top_user(df):
    sessions_per_user = (
        df.groupby("userid")["session_id"]
        .nunique()
        .reset_index()
        .rename(columns={"session_id": "session_count"})
        .sort_values("session_count", ascending=False)
    )
    top_user = sessions_per_user.iloc[0]["userid"]
    top_count = sessions_per_user.iloc[0]["session_count"]
    print(f"Top user: {top_user} with {top_count} sessions")
    return top_user


def build_time_series(df, userid):
    user_df = df[df["userid"] == userid].copy()
    sessions = (
        user_df.groupby("session_id")["ts"]
        .min()
        .reset_index()
        .rename(columns={"ts": "session_start"})
    )
    sessions["week"] = sessions["session_start"].dt.to_period("W").dt.start_time
    weekly = sessions.groupby("week").size().reset_index(name="session_count")
    weekly.columns = ["ds", "y"]
    return weekly


def forecast(weekly_df):
    model = Prophet(weekly_seasonality=True)
    model.fit(weekly_df)
    future = model.make_future_dataframe(periods=13, freq="W")
    forecast_df = model.predict(future)
    return model, forecast_df


def save_results(forecast_df):
    import os
    os.makedirs("output", exist_ok=True)
    forecast_df[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_csv(
        "output/forecast.tsv", sep="\t", index=False
    )
    print("Results saved to output/forecast.tsv")


def main():
    df = load_and_build_sessions(DATA_PATH)
    top_user = get_top_user(df)
    weekly = build_time_series(df, top_user)
    model, forecast_df = forecast(weekly)
    save_results(forecast_df)


if __name__ == "__main__":
    main()
