import time

from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import *
from pyspark.sql.types import *

from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.regression import LinearRegressionModel

kafka_topic_name = "stock"
kafka_bootstrap_servers = "kafka-broker-1:9093,kafka-broker-2:9094,kafka-broker-3:9095"

# Create Spark Session
spark_conn = SparkSession.builder \
    .appName("Real Time Stock Data Processing Project") \
    .config("spark.cassandra.connection.host", "cassandra-1") \
    .config("spark.cassandra.connection.port", "9042") \
    .getOrCreate()

spark_conn.sparkContext.setLogLevel("ERROR")

five_minutes_model = LinearRegressionModel.load("Model/fiveMinutesModel")

ticker_df = spark_conn.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="stock_list", keyspace="vietnam_stock") \
    .load()

# Create StringIndexer for column 'ticker'
string_indexer = StringIndexer(inputCol="ticker", outputCol="ticker_index")

ticker_df = string_indexer.fit(ticker_df).transform(ticker_df)

onehot_encoder = OneHotEncoder(inputCols=["ticker_index"], outputCols=["ticker_encoded"])

ticker_df = onehot_encoder.fit(ticker_df).transform(ticker_df)


def process_real_time_stock_trading_data(json_df):
    json_schema = (StructType()
                   .add("RType", StringType(), False)
                   .add("TradingDate", StringType(), False)
                   .add("Time", StringType(), False)
                   .add("Symbol", StringType(), False)
                   .add("Open", DoubleType(), False)
                   .add("High", DoubleType(), False)
                   .add("Low", DoubleType(), False)
                   .add("Close", DoubleType(), False)
                   .add("Volume", DoubleType(), True)
                   .add("Value", DoubleType(), False))

    stock_df = json_df.select(json_df['offset'], from_json(col("value"), json_schema).alias("data")).selectExpr(
        "offset", "data.*")

    stock_df = stock_df.withColumn("TradingDate", to_date(stock_df['TradingDate'], "dd/MM/yyyy"))

    stock_df = stock_df.withColumn("trading_time",
                                   concat_ws(" ", stock_df['TradingDate'], stock_df['Time'])
                                   )

    stock_df = stock_df.withColumn("trading_time", col("trading_time").cast(TimestampType()))

    stock_df = stock_df.withColumn("trading_time", date_format(stock_df['trading_time'], "yyyy-MM-dd HH:mm:ss"))

    stock_df = stock_df.withColumnRenamed("Symbol", "ticker") \
        .withColumnRenamed("Open", "open") \
        .withColumnRenamed("High", "high") \
        .withColumnRenamed("Low", "low") \
        .withColumnRenamed("Close", "close") \
        .withColumnRenamed("Volume", "volume") \
        .withColumnRenamed("offset", "id")

    return stock_df


def run_aggregation_task(aggregation_df):
    aggregation_df = aggregation_df \
        .withWatermark("trading_time", "5 minutes") \
        .groupBy(col("ticker"), window("trading_time", "1 minute", "1 minute")) \
        .agg(
            first("open").alias("open"),
            max("high").alias("high"),
            min("low").alias("low"),
            last("close").alias("close"),
            sum("volume").alias("volume")
        )

    aggregation_df1 = aggregation_df.select(
        col("window.start").alias("start_time"),
        col("window.end").alias("end_time"),
        'ticker',
        'open',
        'high',
        'low',
        'close',
        'volume'
    )

    return aggregation_df1


def pre_processing_stock_data(aggregation_df1):
    prediction_df = aggregation_df1.select("end_time", "ticker", "close", "volume")

    prediction_df = prediction_df.withColumnRenamed("end_time", "trading_time") \
        .withColumnRenamed("close", "price")

    prediction_df = prediction_df.withColumn("hour", hour(col("trading_time"))) \
        .withColumn("minute", minute(col("trading_time")))

    time.sleep(1)

    print("Schema of prediction data frame:")

    prediction_df.printSchema()

    return prediction_df


def analyze_trends(prediction_df):
    prediction_df = prediction_df.join(ticker_df, on=["ticker"], how="inner")

    assembler = VectorAssembler(inputCols=['hour', 'minute', 'price', 'ticker_encoded', 'volume'], outputCol='features')

    prediction_df1 = assembler.transform(prediction_df)

    prediction_df2 = five_minutes_model.transform(prediction_df1)

    prediction_df2 = prediction_df2.withColumnRenamed("prediction", "next_five_minutes_price")

    prediction_df2 = prediction_df2.withColumn("next_five_minutes_price", round("next_five_minutes_price", -1))

    prediction_df2 = prediction_df2.withColumn("next_five_minutes_price",
                                               prediction_df2.next_five_minutes_price.cast('int'))

    print("Schema of final prediction data frame:")

    prediction_df2.printSchema()

    prediction_df3 = prediction_df2.select("trading_time", "ticker", "price", "volume", "next_five_minutes_price")

    return prediction_df3


def write_to_real_time_table(df, epoc_id):
    try:
        df.write \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="real_time_stock_trading_data", keyspace="vietnam_stock") \
            .mode("append") \
            .save()

        print("Write real time stock trading to Cassandra table successfully!")
    except Exception as e:
        print(f"Error while writing to Cassandra:{e}")


def write_to_aggregation_table(df, epoc_id):
    try:
        df.write \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="aggregated_stock_trading_data", keyspace="vietnam_stock") \
            .mode("append") \
            .save()

        print("Aggregate stock data successfully!")
    except Exception as e:
        print(f"Error while aggregating data to Cassandra table:{e}")


def write_to_trend_analysis_table(df, epoc_id):
    try:
        df.write \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="stock_trend_analysis_data", keyspace="vietnam_stock") \
            .mode("append") \
            .save()

        print("Analyze trend of stock price successfully!")
    except Exception as e:
        print(f"Error while inserting analyzed data to Cassandra table:{e}")


def run_spark_job():
    df = spark_conn \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", kafka_topic_name) \
        .option("startingOffsets", "earliest") \
        .load()

    print("Schema of the dataframe: ")

    df.printSchema()

    json_df = df.selectExpr("offset", "CAST(value AS STRING)")

    time.sleep(1)

    print("Schema of the json dataframe: ")

    json_df.printSchema()

    stock_df = process_real_time_stock_trading_data(json_df)

    real_time_stock_df = stock_df.select('id', 'trading_time', 'ticker', 'open', 'high', 'low', 'close', 'volume')

    aggregation_df = stock_df.withColumn("trading_time", date_format("trading_time", "yyyy-MM-dd HH:mm:00"))

    aggregation_df = aggregation_df.withColumn("trading_time", to_timestamp("trading_time", "yyyy-MM-dd HH:mm:ss"))

    time.sleep(1)

    print("Schema of aggregation data frame:")

    aggregation_df.printSchema()

    aggregation_df1 = run_aggregation_task(aggregation_df)

    prediction_df = pre_processing_stock_data(aggregation_df1)

    prediction_df1 = analyze_trends(prediction_df)

    real_time_table = real_time_stock_df.writeStream \
        .trigger(processingTime="3 seconds") \
        .outputMode("append") \
        .foreachBatch(write_to_real_time_table) \
        .start()

    aggregation_table = aggregation_df1.writeStream \
        .trigger(processingTime="3 seconds") \
        .outputMode("update") \
        .foreachBatch(write_to_aggregation_table) \
        .start()

    trend_analysis_table = prediction_df1.writeStream \
        .trigger(processingTime="3 seconds") \
        .outputMode("update") \
        .foreachBatch(write_to_trend_analysis_table) \
        .start()

    real_time_table.awaitTermination()

    aggregation_table.awaitTermination()

    trend_analysis_table.awaitTermination()

    spark_conn.stop()


def main():
    run_spark_job()


main()
