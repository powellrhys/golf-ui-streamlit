docker network rm kafka-net

docker network create kafka-net

docker run -d --name zookeeper --network kafka-net -p 2181:2181 `
  -e ZOOKEEPER_CLIENT_PORT=2181 `
  confluentinc/cp-zookeeper:latest

docker run -d --name kafka --network kafka-net -p 9092:9092 `
  -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 `
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 `
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 `
  confluentinc/cp-kafka:latest
