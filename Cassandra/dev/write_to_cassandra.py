import json
import time
import datetime
from cassandra.cluster import Cluster
from kafka import KafkaConsumer


KEYSPACE = "demo"


def create_connection():
    cluster = Cluster(['localhost'], port=9042)

    session = cluster.connect()

    return session


def create_keyspace(session: Cluster.connect):
    session.execute("""
            DROP KEYSPACE IF EXISTS demo;
        """)

    print("creating keyspace...")

    session.execute("""
            CREATE KEYSPACE IF NOT EXISTS demo 
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
        """)

    print("setting keyspace...")
    session.set_keyspace(KEYSPACE)

    print("Keyspace created successfully!")

    time.sleep(2)


def create_table(session: Cluster.connect):
    print("creating table...")

    session.execute("""
            CREATE TABLE IF NOT EXISTS stock_information (
                symbol text,
                timestamps timestamp,
                current_price float,
                change_value float,
                change_rate float,
                high float,
                low float,
                open float,
                previous_price float,
                PRIMARY KEY((symbol, timestamps))
            );
        """)

    print("Table created successfully!")

    time.sleep(2)


def insert_data(session: Cluster.connect, message: dict):
    insert_statement = session.prepare("""
            INSERT INTO stock_information(symbol, timestamps, current_price, change_value, change_rate, open, high, low, previous_price)
            VALUES (?,?,?,?,?,?,?,?,?)
        """)

    session.execute(insert_statement,
                    (message['symbol'],
                     message['timestamps'],
                     message['current_price'],
                     message['change_value'],
                     message['change_rate'],
                     message['open'],
                     message['high'],
                     message['low'],
                     message['previous_price'])
                    )


def main():
    session = create_connection()

    create_keyspace(session)

    create_table(session)

    consumer = KafkaConsumer('demo',
                             bootstrap_servers='localhost:9092',
                             auto_offset_reset='earliest',
                             value_deserializer=lambda x: json.loads(x.decode('utf8')),
                             consumer_timeout_ms=5000)

    for element in consumer:
        message = element.value
        message['timestamps'] = datetime.datetime.strptime(message['timestamps'], "%Y-%m-%d %H:%M:%S")

        insert_data(session, message)

    print("Task completed!")


if __name__ == '__main__':
    main()
