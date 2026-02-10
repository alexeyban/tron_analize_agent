from pyspark.sql import DataFrame
from pyspark.sql import functions as F

def aggregate_wallets(forward_df: DataFrame, reverse_df: DataFrame) -> DataFrame:
    """
    Build wallet-level aggregates from forward and reverse flows.
    """

    outgoing = (
        forward_df
        .groupBy("from_address")
        .agg(
            F.countDistinct("tx_hash").alias("out_tx_count"),
            F.sum("amount").alias("total_out_amount"),
            F.countDistinct("to_address").alias("unique_receivers"),
            F.min("block_timestamp").alias("first_seen_ts"),
            F.max("block_timestamp").alias("last_seen_ts"),
        )
        .withColumnRenamed("from_address", "wallet")
    )

    incoming_sources = (
        reverse_df
        .groupBy("source_from_address")
        .agg(
            F.countDistinct("root_tx_hash").alias("funding_events"),
            F.countDistinct("root_tx_hash").alias("funded_out_txs"),
        )
        .withColumnRenamed("source_from_address", "wallet")
    )

    result = (
        outgoing
        .join(incoming_sources, on="wallet", how="left")
        .fillna(0)
    )

    return result
