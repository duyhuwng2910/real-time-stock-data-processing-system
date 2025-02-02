from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
                        .appName("PySpark Job") \
                        .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

if __name__ == "__main__":
    # df = spark.read.csv("test.csv", header=True, inferSchema=True)
    #
    # df.show()

    ticker_df = spark.read \
        .format("org.apache.spark.sql.cassandra") \
        .options(table="stock_list", keyspace="vietnam_stock") \
        .load()

    spark.stop()
