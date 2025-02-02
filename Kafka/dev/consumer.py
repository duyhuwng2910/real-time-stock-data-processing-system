import json

from kafka import KafkaConsumer

bootstrap_servers = ['localhost:29093', 'localhost:29094', 'localhost:29095']

consumer = KafkaConsumer('stock',
                         bootstrap_servers=bootstrap_servers,
                         auto_offset_reset='earliest',
                         value_deserializer=lambda x: json.loads(x.decode('utf8')),
                         consumer_timeout_ms=10000)

for message in consumer:
    print(message.value)
    
