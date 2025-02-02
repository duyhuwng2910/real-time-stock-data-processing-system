### Spark

# Truy cập vào cửa sổ dòng lệnh của Spark container
docker exec -it spark-master bash

pip install pandas pyarrow cassandra-driver

## Spark Structured Streaming
# Thực thi spark structured streaming application
spark-submit --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 --master spark://spark-master:7077 consumer.py

# Cho mục đích kiểm thử
spark-submit --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 --master spark://spark-master:7077 consumer_dev.py

# Cho mục đích chạy bộ dữ liệu giả lập
spark-submit --jars jars --master spark://spark-master:7077 consumer_simulation.py

# Cho mục đích kiểm thử local
spark-submit --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 --master spark://spark-master:7077 Spark/dev/consumer.py

## Spark ML
spark-submit trend_analysis.py

## Cho mục đích kiểm thử local
spark-submit Spark/trend_analysis.py