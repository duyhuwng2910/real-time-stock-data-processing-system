import datetime
import random
import json
import sys

import pandas as pd

from kafka import KafkaProducer

from cassandra.cluster import Cluster

import vnstock_data

# Uncomment if you use Windows
# sys.path.append(r'W:/Study/UET/Graduation Thesis/Real-time-stock-data-processing-system/SSI')

# Uncomment if you use Ubuntu
sys.path.append(r'/home/nguyenduyhung/graduation_thesis/Real-Time-Stock-Data-Processing-System/SSI')

import config

vnstock_client = client = vnstock_data.ssi.fc_md_client.MarketDataClient(config)

bootstrap_servers = ['localhost:29093', 'localhost:29094', 'localhost:29095']

producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

cluster = Cluster(['localhost'], port=9042)

session = cluster.connect()

session.set_keyspace("vietnam_stock")


def pandas_factory(colnames, rows):
    """
        Function to get pyspark pandas dataframe
        from a query in Cassandra table
    """
    return pd.DataFrame(rows, columns=colnames)


session.row_factory = pandas_factory

session.default_fetch_size = 10000000


def insert_ticker_list(ticker_df):
    print("Starting to get the list of ticker to extract data...")

    session.execute("TRUNCATE TABLE stock_list;")

    insert_statement = session.prepare("INSERT INTO stock_list (ticker) VALUES (?)")

    try:
        for row in ticker_df.itertuples(index=False):
            values = tuple(row)  # Convert DataFrame row to tuple

            session.execute(insert_statement, values)

        print("Insert list of ticker successfully!")

    except Exception as e:
        print(f"Error while inserting ticker list: {e}")


price_df = pd.read_csv('stock_data.csv')

# Return the data of ticker list in VN100
ticker_df = vnstock_data.ssi.get_index_component(client, config, index='VN100', page=1, pageSize=100)

ticker_df = ticker_df.rename(columns={"StockSymbol": "ticker"})

# Uncomment if using dataset of HOSE tickers list
ticker_list = ticker_df['ticker'].to_list()

insert_ticker_list(ticker_df)

today = str(datetime.date.today())
hour = datetime.datetime.now().hour
rtype = 'B'

volume_list = [10, 20, 30, 40, 50, 60, 70, 80, 90,
               100, 200, 300, 400, 500, 600, 700, 800, 900,
               1000]


def send_data_to_kafka(start, num):
    while start <= 500:
        minute = datetime.datetime.now().minute
        second = datetime.datetime.now().second
        trading_time = str(hour) + ":" + str(minute) + ":" + str(second)

        for i in range(num):
            symbol = random.choice(ticker_list)

            price = price_df.loc[price_df['ticker'] == symbol, 'close'].iloc[0]

            open_price = round(random.randint(price - 3000, price + 3000), -1)

            high = low = close = open_price

            volume = random.choice(volume_list)

            data = {
                'RType': rtype,
                'TradingDate': today,
                'Time': trading_time,
                'Symbol': symbol,
                'Open': open_price,
                'High': high,
                'Low': low,
                'Close': close,
                'Volume': volume,
                'Value': 0
            }

            producer.send("stock", value=data)

        start += 1


def main():
    send_data_to_kafka(0, 10000)


if __name__ == "__main__":
    main()
