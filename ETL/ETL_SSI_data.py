import threading
import pandas as pd
import datetime
import time
import os
from collections import OrderedDict

import mysql.connector
from sqlalchemy import create_engine

import vnstock_data
import sys

# Uncomment if you use Windows
sys.path.append(r'W:/Study/UET/Graduation Thesis/Real-time-stock-data-processing-system/SSI')

# Uncomment if you use Ubuntu
# sys.path.append(r'/home/nguyenduyhung/graduation_thesis/project/SSI')

import config

connection = mysql.connector.connect(user='root',
                                     password='root',
                                     host='localhost',
                                     database='vietnam_stock')

cursor = connection.cursor()

# Create a SQLAlchemy engine to connect to the MySQL database
engine = create_engine("mysql+mysqlconnector://root:root@localhost/vietnam_stock")


def extract_daily_ohlcv_data(df: pd.DataFrame):
    """
        Function to get stock historical data of symbols in a specified exchange
    """
    ticker_df = df['ticker']

    error_df = pd.DataFrame({'ticker': []})

    exchange = df.iloc[0, df.columns.get_loc('exchange')].lower()

    exchange_name = exchange.upper()

    columns = ['time', 'ticker', 'open', 'high', 'low', 'close', 'volume']

    dtypes = {
        'time': 'object',
        'ticker': 'object',
        'open': 'int64',
        'high': 'int64',
        'low': 'int64',
        'close': 'int64',
        'volume': 'int64'
    }

    exchange_df = pd.DataFrame(columns=columns)

    # Set data types for the columns
    for column, dtype in dtypes.items():
        exchange_df[column] = exchange_df[column].astype(dtype)

    for ticker in ticker_df:
        start_date = df.loc[df['ticker'] == ticker].iloc[0]['first_trading_date']

        try:
            historical_data = vnstock_data.stock_historical_data(symbol=ticker,
                                                                 start_date=start_date,
                                                                 end_date=str(datetime.date.today()),
                                                                 resolution='1D',
                                                                 type='stock',
                                                                 beautify=True,
                                                                 decor=False,
                                                                 source='SSI')

            historical_data['time'] = pd.to_datetime(historical_data['time'])
            
            historical_data = historical_data.loc[:, ['time', 'ticker', 'open', 'high', 'low', 'close', 'volume']]

            try:
                exchange_df = pd.concat([exchange_df, historical_data])

                print(f"Inserting data of symbol {ticker}")

            except Exception as e:
                print(f"Error while concat data frame:{e}")

        except KeyError:
            print(f"Key error with {ticker}")

            error_df.loc[len(error_df), 'ticker'] = ticker

            continue
        except pd.errors.IntCastingNaNError:
            print(f"NA error with {ticker}")

            error_df.loc[len(error_df), 'ticker'] = ticker

            continue

    try:
        exchange_df.to_sql(f'historical_stock_data_one_day_{exchange}',
                           con=engine,
                           if_exists='append',
                           index=False)

        print(f"Insert historical stock data of exchange {exchange_name} completely!")

    except Exception as e:
        print(f"Error here:{e}")

    time.sleep(5)

    current_dir = os.getcwd()

    # Uncomment if using Windows
    error_csv_file_path = os.path.join(current_dir,
                                       'Excel files',
                                       f'Error files\historical_stock_data_{exchange_name}_{datetime.date.today()}.csv')

    # Uncomment if using Ubuntu
    # error_csv_file_path = os.path.join(current_dir,
    #                                    'Excel files',
    #                                    f'Error files/historical_stock_data_{exchange_name}_{datetime.date.today()}.csv')

    error_df.to_csv(error_csv_file_path)

    print("Update error symbols list file successfully!")


def extract_daily_historical_stock_data(exchange_df_list: list):
    """
        Function to get stock historical data of all of Vietnam Stock Market
    """
    print("Starting extracting historical stock data...")
    
    threads_list = []

    for exchange_df in exchange_df_list:
        thread = threading.Thread(target=extract_daily_ohlcv_data, args=(exchange_df,))

        threads_list.append(thread)

        thread.start()

    for thread in threads_list:
        thread.join()
    
    time.sleep(5)

    print("Insert daily historical stock data of Vietnam Stock Market successfully!")


def extract_intraday_ohlcv_data(df: pd.DataFrame, trading_date: str):
    """
        Function to get the intraday stock data of symbols in a specified exchange
    """
    ticker_df = df['ticker']

    error_df = pd.DataFrame({'ticker': []})

    exchange = df.iloc[0, df.columns.get_loc('exchange')]

    columns = ['time', 'ticker', 'open', 'high', 'low', 'close', 'volume']

    dtypes = {
        'time': 'object',
        'ticker': 'object',
        'open': 'int64',
        'high': 'int64',
        'low': 'int64',
        'close': 'int64',
        'volume': 'int64'
    }

    exchange_df = pd.DataFrame(columns=columns)

    # Set data types for the columns
    for column, dtype in dtypes.items():
        exchange_df[column] = exchange_df[column].astype(dtype)

    for ticker in ticker_df:
        try:
            intraday_data = vnstock_data.stock_historical_data(symbol=ticker,
                                                               start_date=str(trading_date),
                                                               end_date=str(trading_date),
                                                               resolution='1',
                                                               type='stock',
                                                               beautify=True,
                                                               decor=False,
                                                               source='SSI')
            if intraday_data.shape[0] > 0:
                try:
                    exchange_df = pd.concat([exchange_df, intraday_data])

                    print(f"Inserting data of symbol {ticker}")
                except Exception as e:
                    print(f"Error while concat data frame:{e}")

        except Exception as e:
            print(f"Error while extracting intraday data of symbol {ticker}:{e}")

            error_df.loc[len(error_df), 'ticker'] = ticker

            continue

    try:
        exchange_df = exchange_df.loc[:, ['time', 'ticker', 'open', 'high', 'low', 'close', 'volume']]
        
        exchange_df.to_sql('intraday_stock_data', con=engine, if_exists='append', index=False)

        print(f"Insert intraday stock data of exchange {exchange} completely!")
    
    except Exception as e:
        print(f"Error while inserting data: {e}")

    time.sleep(5)

    current_dir = os.getcwd()

    # Uncomment if using Ubuntu
    # error_csv_file_path = os.path.join(current_dir, 'Excel files', f'Error files/intraday_stock_data_{exchange}.csv')

    # Uncomment if using Windows
    error_csv_file_path = os.path.join(current_dir, 'Excel files', f'Error files\intraday_stock_data_{exchange}.csv')

    error_df.to_csv(error_csv_file_path)

    print("Update error symbols list file successfully!")


def get_latest_trading_date():
    """
        Function to return the latest trading date, according the time running this function
    """
    today = datetime.date.today()

    weekday = today.weekday()

    # Nếu là thứ Bảy hoặc Chủ Nhật, trả về ngày thứ Sáu của tuần đó
    if weekday == 5:
        return today - datetime.timedelta(days=1)
    elif weekday == 6:
        return today - datetime.timedelta(days=2)
    else:
        now = datetime.datetime.now()

        if now.hour >= 15 and now.minute >= 30:
            return today
        else:
            if weekday == 0:
                return today - datetime.timedelta(days=3)
            else:
                return today - datetime.timedelta(days=1)


def extract_intraday_stock_data(exchange_list: list):
    """
        Function to get the intraday stock data of all of Vietnam Stock Market
    """
    print("Starting extracting intraday stock data...")
    
    latest_trading_date = get_latest_trading_date()

    threads_list = []

    for exchange in exchange_list:
        thread = threading.Thread(target=extract_intraday_ohlcv_data, args=(exchange, latest_trading_date))

        threads_list.append(thread)

        thread.start()

    for thread in threads_list:
        thread.join()

    time.sleep(5)

    print("Insert intraday stock data of Vietnam Stock Market successfully!")


def aggregate_intraday_stock_data(ticker_df: pd.DataFrame, ticker: str):
    """
        Function to aggregate the intraday stock data
    """
    ticker_df['time'] = pd.to_datetime(ticker_df['time'])

    ticker_df.set_index('time', inplace=True)

    ohlc_df = ticker_df.resample('5mins', label='left', closed='right').agg(
        OrderedDict([
            ('open', 'first'),
            ('high', 'max'),
            ('low', 'min'),
            ('close', 'last'),
            ('volume', 'sum')
        ])
    )

    ohlc_df = ohlc_df.assign(ticker=ticker)

    ohlc_df = ohlc_df.reset_index()
    
    ohlc_df['time'] = pd.to_datetime(ohlc_df['time'])
    
    ohlc_df = ohlc_df.fillna(0)
    
    ohlc_df = ohlc_df.astype(
        {
            "open": "int",
            "high": "int",
            "low": "int",
            "close": "int"
        }
    )
    
    ohlc_df = ohlc_df.loc[:, ['time', 'ticker', 'open', 'high', 'low', 'close', 'volume']]
    
    try:
        ohlc_df.to_sql("intraday_stock_data_five_mins", engine, if_exists='append', index=False)
    
        print(f"Insert aggregation data of {ticker} successfully!")

    except Exception as e:
        print(f"Error while inserting aggregation data of {ticker}: {e}")


def main():
    # Uncomment the below line if you use Ubuntu
    # df = pd.read_excel('/home/nguyenduyhung/graduation_thesis/project/Excel files/vn_stock.xlsx', sheet_name='Stock')

    # Uncomment the below line if you use Windows
    df = pd.read_excel(
        'W:/study/UET/Graduation Thesis/Real-time-stock-data-processing-system/Excel files/vn_stock.xlsx',
        sheet_name='Stock')

    df['first_trading_date'] = df['first_trading_date'].dt.strftime('%Y-%m-%d')

    hose_df = df.loc[df['exchange'] == 'HOSE']

    hnx_df = df.loc[df['exchange'] == 'HNX']

    upcom_df = df.loc[df['exchange'] == 'UPCOM']

    exchange_df_list = [hose_df, hnx_df, upcom_df]

    cursor.execute('''
                    DROP TABLE IF EXISTS historical_stock_data_one_day_hose;

                    CREATE TABLE historical_stock_data_one_day_hose (
                        `time` DATETIME,
                        ticker VARCHAR(20),
                        `open` INTEGER,
                        high INTEGER,
                        low INTEGER,
                        `close` INTEGER,
                        volume BIGINT
                    );

                    DROP TABLE IF EXISTS historical_stock_data_one_day_hnx;

                    CREATE TABLE historical_stock_data_one_day_hnx (
                        `time` DATETIME,
                        ticker VARCHAR(20),
                        `open` INTEGER,
                        high INTEGER,
                        low INTEGER,
                        `close` INTEGER,
                        volume BIGINT
                    );

                    DROP TABLE IF EXISTS historical_stock_data_one_day_upcom;

                    CREATE TABLE historical_stock_data_one_day_upcom (
                        `time` DATETIME,
                        ticker VARCHAR(20),
                        `open` INTEGER,
                        high INTEGER,
                        low INTEGER,
                        `close` INTEGER,
                        volume BIGINT
                    );
                    
                    DROP TABLE IF EXISTS intraday_stock_data;

                    CREATE TABLE intraday_stock_data (
                        `time` DATETIME,
                        ticker VARCHAR(20),
                        `open` INTEGER,
                        high INTEGER,
                        low INTEGER,
                        `close` INTEGER,
                        volume BIGINT,
                    );
                    
                    DROP TABLE IF EXISTS intraday_stock_data_five_mins;

                    CREATE TABLE intraday_stock_data_five_mins (
                        `time` DATETIME,
                        ticker VARCHAR(20),
                        `open` INTEGER,
                        high INTEGER,
                        low INTEGER,
                        `close` INTEGER,
                        volume BIGINT,               
                    );
                   ''')
    
    extract_daily_historical_stock_data(exchange_df_list)
    
    time.sleep(3)

    extract_intraday_stock_data(exchange_df_list)
    
    cursor.close()
    
    connection.close()


main()
