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