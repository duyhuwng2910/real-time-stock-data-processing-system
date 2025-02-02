import time
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

import mysql.connector
from sqlalchemy import create_engine

kafka_topic_name = "hose"
kafka_bootstrap_servers = "kafka-broker-1:9093"

connection = mysql.connector.connect(user='root',
                                     password='root',
                                     host='mysql',
                                     database='vietnam_stock')

cursor = connection.cursor()

# Create a SQLAlchemy engine to connect to the MySQL database
engine = create_engine("mysql+mysqlconnector://root:root@localhost/vietnam_stock")

jdbc_url = "jdbc:mysql://mysql:3306/vietnam_stock"

db_credentials = {
    "user": "root",
    "password": "root",
    "driver": "com.mysql.cj.jdbc.Driver"
}


def write_to_real_time_data_table(df, epoc_id):
    df.write \
        .jdbc(url=jdbc_url,
              table="real_time_stock_trading_data",
              mode="append",
              properties=db_credentials)


def write_to_aggregation_table(df, epoc_id):
    df.write \
        .jdbc(url=jdbc_url,
              table="real_time_stock_trading_data_one_min",
              mode="append",
              properties=db_credentials)


if __name__ == "__main__":
    cursor.execute("DELETE FROM real_time_stock_trading_data_one_min;")
    
    connection.commit()
    
    truncate_min = udf(lambda dt: datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute), TimestampType())
    
    # Create Spark Session
    spark_conn = SparkSession.builder.appName("Real Time Stock Data Processing Demo") \
        .master("local[*]") \
        .config('spark.jars.packages', 'com.mysql:mysql-connector-j:8.3.0,org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0') \
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

    time.sleep(1)

    json_df = df.selectExpr("offset", "CAST(value AS STRING)")

    print("Schema of the json dataframe: ")

    json_df.printSchema()
    
    time.sleep(1)
    
    json_schema = (StructType()
                   .add("trading_time", StringType(), False)
                   .add("ticker", StringType(), False)
                   .add("open", DoubleType(), False)
                   .add("high", DoubleType(), False)
                   .add("low", DoubleType(), False)
                   .add("close", DoubleType(), False)
                   .add("volume", DoubleType(), True))

    stock_df = json_df.select(json_df['offset'], from_json(col("value"), json_schema).alias("data")).selectExpr("offset", "data.*")
    
    stock_df1 = stock_df.withColumn("trading_time", to_timestamp("trading_time", "yyyy-MM-dd HH:mm:ss"))

    stock_df1.printSchema()

    stock_df1 = stock_df1.withColumnRenamed("offset", "id")

    real_time_stock_df = stock_df1.select('id', 'trading_time', 'ticker', 'open', 'high', 'low', 'close', 'volume')

    aggregation_df = stock_df1.withColumn("trading_time", truncate_min("trading_time"))
    
    aggregation_df = aggregation_df \
        .withWatermark("trading_time", "10 minutes") \
        .groupBy("ticker", window("trading_time", "1 minute", "1 minute").alias("trading_time")) \
        .agg(
            first("open").alias("open"),
            max("high").alias("high"),
            min("low").alias("low"),
            last("close").alias("close"),
            sum("volume").alias("volume")
        )
    
    aggregation_df = aggregation_df.select('trading_time', 'ticker', 'open', 'high', 'low', 'close', 'volume')
    
    real_time_stock_data = real_time_stock_df.writeStream \
        .foreachBatch(write_to_real_time_data_table) \
        .trigger(processingTime="10 seconds") \
        .outputMode("append") \
        .start()

    aggregation_df.writeStream \
        .foreachBatch(write_to_aggregation_table) \
        .trigger(processingTime="15 seconds") \
        .outputMode("append") \
        .start()
    
    real_time_stock_data.awaitTermination()

    aggregation_df.awaitTermination()
    
    print("Task completed!")
    
    connection.close()