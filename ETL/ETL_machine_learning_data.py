import sys
import datetime
import time

from cassandra.cluster import Cluster

import pandas as pd

import vnstock_data

# Uncomment if you use Windows
sys.path.append(r'W:/Study/UET/Graduation Thesis/Real-time-stock-data-processing-system/SSI')

# Uncomment if you use Ubuntu
# sys.path.append(r'/home/nguyenduyhung/graduation_thesis/Real-Time-Stock-Data-Processing-System/SSI')

import config

client = vnstock_data.ssi.fc_md_client.MarketDataClient(config)

cluster = Cluster(['localhost'], port=9042)

session = cluster.connect()

session.set_keyspace("vietnam_stock")

ticker_df = vnstock_data.ssi.get_index_component(client, config, index='VN100', page=1, pageSize=100)

ticker_df = ticker_df.rename(columns={'StockSymbol': 'ticker'})

today = datetime.date.today()

start_date = today - datetime.timedelta(days=30)


def insert_ticker_list():
    print("Starting to get the ticker list...")

    session.execute("TRUNCATE TABLE stock_list;")

    insert_statement = session.prepare("INSERT INTO stock_list (ticker) VALUES (?)")

    try:
        for ticker in ticker_df.itertuples(index=False):
            values = tuple(ticker)  # Convert DataFrame row to tuple

            session.execute(insert_statement, values)

        print("Insert list of ticker successfully!")

    except Exception as e:
        print(f"Error while inserting ticker list: {e}")


def extract_machine_learning_data():
    print("Starting to extract the stock data of ticker list in last 90 days for machine learning purpose")

    session.execute("TRUNCATE TABLE stock_data_for_ml;")

    for ticker in ticker_df['ticker']:
        intraday_data = vnstock_data.stock_historical_data(symbol=ticker,
                                                           start_date=str(start_date),
                                                           end_date=str(today),
                                                           resolution='1',
                                                           type='stock',
                                                           beautify=True,
                                                           decor=False,
                                                           source='DNSE')

        ticker_data = intraday_data[['time', 'ticker', 'close', 'volume']]

        ticker_data = ticker_data.rename(columns={"time": "trading_time", "close": "price"})

        ticker_data['trading_time'] = pd.to_datetime(ticker_data['trading_time'])

        ticker_data['trading_time'] = ticker_data['trading_time'].dt.ceil(freq='min')

        length = len(ticker_data)

        new_cols = {
            'next_five_minutes_price': 0
        }

        ticker_data = ticker_data.assign(**new_cols)

        for i in range(0, length, 1):
            if i < length - 5:
                ticker_data.loc[i, "next_five_minutes_price"] = ticker_data.loc[i + 5, "price"]

        insert_ml_statement = session.prepare("""
                                            INSERT INTO stock_data_for_ml 
                                                (trading_time, ticker, price, volume, next_five_minutes_price)
                                            VALUES (?,?,?,?,?)
                                           """)

        # Iterate through DataFrame rows and insert values
        try:
            for row in ticker_data.itertuples(index=False):
                values = tuple(row)  # Convert DataFrame row to tuple:

                session.execute(insert_ml_statement, values)

            print(f"Insert intraday data of {ticker} completely!")

        except Exception as err:
            print("Error while inserting row:", err)


def main():
    insert_ticker_list()

    time.sleep(1)

    extract_machine_learning_data()

    time.sleep(1)

    print("Extract successfully!")


if __name__ == '__main__':
    main()
