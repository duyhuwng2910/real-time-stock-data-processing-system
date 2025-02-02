from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *


kafka_topic_name = "demo"
kafka_bootstrap_servers = "localhost:9094"


if __name__ == "__main__":
    # Create Spark Session
    spark_conn = SparkSession.builder.appName("Real Time Stock Data Processing Demo") \
        .master("local[*]") \
        .config('spark.jars.packages', 'org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.0') \
        .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0') \
        .getOrCreate()

    spark_conn.sparkContext.setLogLevel("ERROR")

    # Construct a streaming DataFrame to connect Spark Structured Streaming
    # with Kafka topic to read Data Streams
    df = spark_conn \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", kafka_topic_name) \
        .option("startingOffsets", "latest") \
        .load()

    print("Schema of the dataframe: ")

    df.printSchema()

    # Step 3: Extract topic information and apply suitable schema
    stock_df = df.selectExpr("CAST(value as STRING)")

    # Define a schema for the data
    stock_schema = StructType() \
        .add("symbol", StringType()) \
        .add("timestamps", TimestampType()) \
        .add("current_price", DoubleType()) \
        .add("change_value", DoubleType()) \
        .add("change_rate", DoubleType()) \
        .add("open", DoubleType()) \
        .add("high", DoubleType()) \
        .add("low", DoubleType()) \
        .add("previous_price", DoubleType())

    # Chọn ra các cột từ dataframe JSON
    stock_df1 = stock_df \
        .select(from_json(col("value"), stock_schema)
                .alias("stock_data"))

    stock_df2 = stock_df1.select("stock_data.*")

    print(stock_df2)

    # print the dataframe in console for debug purpose
    streaming_query = stock_df2.writeStream \
        .trigger(processingTime='5 seconds') \
        .outputMode("update") \
        .format('console') \
        .option("truncate", "false") \
        .start()

    streaming_query.awaitTermination(5)

    print("Task completed!")
