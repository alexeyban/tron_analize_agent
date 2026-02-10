from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp

def ensure_table(spark: SparkSession, table_name: str, schema_df, partition_by=None):
    if not spark._jsparkSession.catalog().tableExists(table_name):
        writer = schema_df.write.format("delta")
        if partition_by:
            writer = writer.partitionBy(*partition_by)
        writer.saveAsTable(table_name)

def merge_idempotent(
    spark: SparkSession,
    source_df,
    target_table: str,
    pk_cols: list
):
    if not spark._jsparkSession.catalog().tableExists(target_table):
        source_df.write.format("delta").saveAsTable(target_table)
        return

    target = DeltaTable.forName(spark, target_table)
    cond = " AND ".join([f"t.{c} = s.{c}" for c in pk_cols])

    (target.alias("t")
        .merge(source_df.alias("s"), cond)
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute())
