docker network create vietnam-stock

#
# If you want to run without monitoring
#
docker compose up -d

### For monitoring purpose
# start kafka
docker compose -f Kafka/docker-compose.yaml up -d

# Start other containers
docker compose up -f docker-compose-monitor-ver.yaml up -d

# Start monitoring containers
docker compose -f Monitor/docker-compose.yaml up -d
