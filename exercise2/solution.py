from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

DATA_PATH = "data/userid-timestamp-artid-artname-traid-traname.tsv"

def create_spark_session():
    return (
        SparkSession.builder
        .appName("music-behaviour-analytics")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )

def load_data(spark):
    df = (
        spark.read
        .option("sep", "\t")
        .option("header", "false")
        .csv(DATA_PATH)
        .toDF("userid", "timestamp", "artistid", "artist_name", "trackid", "track_name")
    )
    df = df.withColumn("ts", F.to_timestamp("timestamp", "yyyy-MM-dd'T'HH:mm:ss'Z'"))
    df = df.filter(F.col("ts").isNotNull() & F.col("userid").isNotNull() & F.col("track_name").isNotNull())
    return df

def assign_sessions(df):
    user_window = Window.partitionBy("userid").orderBy("ts")

    df = (
        df
        .withColumn("prev_ts", F.lag("ts").over(user_window))
        .withColumn("gap_min", (F.unix_timestamp("ts") - F.unix_timestamp("prev_ts")) / 60)
        .withColumn(
            "is_new_session",
            F.when(
                F.col("prev_ts").isNull() | (F.col("gap_min") > 20), 1
            ).otherwise(0)
        )
        .withColumn("session_id", F.sum("is_new_session").over(user_window))
    )

    return df

def get_top_sessions(df):
    session_lengths = (
        df
        .groupBy("userid", "session_id")
        .agg(F.count("*").alias("track_count"))
    )

    rank_window = Window.orderBy(F.col("track_count").desc())
    ranked = session_lengths.withColumn("rank", F.rank().over(rank_window))

    return ranked.filter(F.col("rank") <= 50)

def get_top_songs(df, top_sessions):
    return (
        df
        .join(top_sessions.select("userid", "session_id"), on=["userid", "session_id"])
        .groupBy("artist_name", "track_name")
        .agg(F.count("*").alias("occurrences"))
        .orderBy(F.col("occurrences").desc())
        .limit(10)
    )


def save_results(results):
    import os
    os.makedirs("output", exist_ok=True)
    with open("output/top10_songs.tsv", "w", encoding="utf-8") as f:
        f.write("rank\tartist_name\ttrack_name\toccurrences\n")
        for i, row in enumerate(results, 1):
            f.write(f"{i}\t{row.artist_name}\t{row.track_name}\t{row.occurrences}\n")


def main():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    df = load_data(spark)
    df = assign_sessions(df)

    top_sessions = get_top_sessions(df)
    top_songs = get_top_songs(df, top_sessions)

    top_songs.show(truncate=False)
    save_results(top_songs.collect())

    spark.stop()


if __name__ == "__main__":
    main()