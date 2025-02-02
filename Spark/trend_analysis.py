import time

import pyspark.pandas as ps_pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

from cassandra.cluster import Cluster

# Create cluster

# Uncomment if running in console
# cluster = Cluster(['localhost'], port=9042)
# Uncomment when run in docker container
cluster = Cluster(['cassandra-1', 'cassandra-2', 'cassandra-3'], port=9042)

session = cluster.connect()

session.set_keyspace("vietnam_stock")

spark = SparkSession.builder.appName("Linear Regression model building application").getOrCreate()

spark.sparkContext.setLogLevel("ERROR")


def pandas_factory(colnames, rows):
    """
        Function to get pyspark pandas dataframe
        from a query in Cassandra table
    """
    return ps_pd.DataFrame(rows, columns=colnames)


session.row_factory = pandas_factory

session.default_fetch_size = 10000000

# Return the data of all ticker in HOSE exchange
ticker_df = session.execute("SELECT * FROM stock_list;")

ticker_df = ticker_df._current_rows


def read_cassandra_table(ticker_df):
    stock_data = ps_pd.DataFrame(columns={
        "trading_time": 'datetime',
        "ticker": 'str',
        "price": 'int',
        "volume": 'int',
        "next_five_minutes_price": 'int'
    })

    query_statement = session.prepare("SELECT * FROM stock_data_for_ml WHERE ticker = (?);")

    try:
        for ticker in ticker_df.itertuples(index=False):
            values = tuple(ticker)  # Convert DataFrame row to tuple

            dataset = session.execute(query_statement, values)

            ps_df = dataset._current_rows

            stock_data = ps_pd.concat([stock_data, ps_df])

        print("Insert data for building model successfully!")

        return stock_data

    except Exception as e:
        print(f"Error while inserting ticker list: {e}")


def build_five_minutes_linear_regression_model(training_data):
    print("Started to build model...")
    
    five_mins_lr = LinearRegression(featuresCol="features", labelCol="next_five_minutes_price")

    five_mins_model = five_mins_lr.fit(training_data)

    return five_mins_model


def five_minutes_prediction(five_mins_model, testing_data):
    print("Started to predict the testing data...")
    
    five_mins_prediction = five_mins_model.transform(testing_data)

    return five_mins_prediction


def evaluate_five_minutes_linear_regression_model(five_mins_prediction):
    """
        Evaluate the model for predicting stock index in next five minutes
    """
    print("Started to evaluate the model...")
    
    five_mins_evaluator_r2 = RegressionEvaluator(labelCol="next_five_minutes_price", predictionCol="prediction",
                                                 metricName="r2")

    five_mins_r2 = five_mins_evaluator_r2.evaluate(five_mins_prediction)

    five_mins_evaluator_rmse = RegressionEvaluator(labelCol="next_five_minutes_price", predictionCol="prediction",
                                                   metricName="rmse")

    five_mins_rmse = five_mins_evaluator_rmse.evaluate(five_mins_prediction)

    five_mins_evaluator_mae = RegressionEvaluator(labelCol="next_five_minutes_price", predictionCol="prediction",
                                                  metricName="mae")

    five_mins_mae = five_mins_evaluator_mae.evaluate(five_mins_prediction)

    return [five_mins_r2, five_mins_rmse, five_mins_mae]


def main():
    ps_df = read_cassandra_table(ticker_df)
    
    time.sleep(1)
    
    print("Started to accomplish dataset...")
    
    ps_df['trading_date'] = ps_df['trading_time'].dt.date

    ps_df['time'] = ps_df['trading_time'].dt.strftime('%H:%M:%S').astype('str')

    stock_data = ps_df[['trading_date', 'time', 'ticker', 'price', 'volume', 'next_five_minutes_price']]

    stock_data = stock_data.to_spark()

    # Preprocess timestamp features
    stock_data = stock_data.withColumn("hour", hour(col("time"))) \
        .withColumn("minute", minute(col("time")))

    # Create StringIndexer for column 'ticker'
    string_indexer = StringIndexer(inputCol="ticker", outputCol="ticker_index")

    stock_data = string_indexer.fit(stock_data).transform(stock_data)

    onehot_encoder = OneHotEncoder(inputCols=["ticker_index"], outputCols=["ticker_encoded"])

    stock_data = onehot_encoder.fit(stock_data).transform(stock_data)

    assembler = VectorAssembler(inputCols=['hour', 'minute', 'price', 'ticker_encoded', 'volume'], outputCol='features')

    stock_transformed_data = assembler.transform(stock_data)

    (training_data, testing_data) = stock_transformed_data.randomSplit([0.8, 0.2], seed=42)

    five_mins_model = build_five_minutes_linear_regression_model(training_data)

    five_mins_prediction = five_minutes_prediction(five_mins_model, testing_data)

    five_mins_model_evaluation = evaluate_five_minutes_linear_regression_model(five_mins_prediction)

    data = [
            {'model': 'next five minutes price prediction',
             'r2': five_mins_model_evaluation[0],
             'rmse': five_mins_model_evaluation[1],
             'mae': five_mins_model_evaluation[2]}]

    evaluation_df = ps_pd.DataFrame(data)

    print("Evaluate model: ")

    print(evaluation_df)

    try:
        five_mins_model.write().overwrite().save("Model/fiveMinutesModel/")

        print("Five minutes model is saved sucessfully!")
    except Exception as e:
        print(f"Error while saving five minutes model:{e}")

    five_mins_prediction.select("price", "next_five_minutes_price", "prediction").limit(10).show()

    # Stop spark session
    spark.stop()


if __name__ == "__main__":
    print("Started to build model for predicting stock price in next 5 minutes...")

    main()
