### Kafka
# Truy cập vào cửa sổ dòng lệnh của Kafka broker
docker exec -it kafka-broker-1 bash

## Tạo kafka topic
# Ở đây, tạo một topic với số replication factor là 2 và partitions là 3
kafka-topics --create --topic stock --bootstrap-server kafka-broker-1:9093 --replication-factor 2 --partitions 3

# Nếu khởi chạy cụm Kafka on production thì chạy dòng sau
kafka-topics --create --topic stock --bootstrap-server kafka-controller-1:9092 --replication-factor 3 --partitions 4

# Kiểm tra danh sách các topic có trong hệ thống
kafka-topics --list --bootstrap-server kafka-broker-1:9093

# Kiểm tra thông tin về topic đã tạo
kafka-topics --describe --topic stock --bootstrap-server kafka-broker-1:9093

# Kiểm tra bản tin được gửi lên topic
kafka-console-consumer --topic stock --bootstrap-server kafka-broker-1:9093
