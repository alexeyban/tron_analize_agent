from pyspark.sql import DataFrame
from pyspark.sql.functions import col

def not_null(df: DataFrame, cols):
    for c in cols:
        df = df.filter(col(c).isNotNull())
    return df

def positive_amount(df: DataFrame, col_name="amount"):
    return df.filter(col(col_name) > 0)

def deduplicate(df: DataFrame, pk_cols):
    return df.dropDuplicates(pk_cols)
