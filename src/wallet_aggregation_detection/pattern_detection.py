import json
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

def load_thresholds(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def detect_suspicious_patterns(wallet_df: DataFrame, thresholds: dict) -> DataFrame:
    """
    Rule-based suspicious wallet detection.
    """

    df = wallet_df

    df = df.withColumn(
        "flag_high_volume",
        F.col("total_out_amount") >= thresholds["high_out_amount"]
    )

    df = df.withColumn(
        "flag_many_receivers",
        F.col("unique_receivers") >= thresholds["many_receivers"]
    )

    df = df.withColumn(
        "activity_window_sec",
        (F.col("last_seen_ts") - F.col("first_seen_ts")) / 1000
    )

    df = df.withColumn(
        "flag_rapid_activity",
        F.col("activity_window_sec") <= thresholds["rapid_activity_seconds"]
    )

    df = df.withColumn(
        "fan_out_ratio",
        F.when(F.col("out_tx_count") > 0,
               F.col("unique_receivers") / F.col("out_tx_count"))
         .otherwise(0)
    )

    df = df.withColumn(
        "flag_fan_out",
        F.col("fan_out_ratio") >= thresholds["fan_out_ratio"]
    )

    df = df.withColumn(
        "is_suspicious",
        F.col("flag_high_volume")
        | F.col("flag_many_receivers")
        | F.col("flag_rapid_activity")
        | F.col("flag_fan_out")
    )

    return df
