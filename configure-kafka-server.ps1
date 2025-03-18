# Function to check if a container exists and remove it
function Remove-ContainerIfExists {
    param (
        [string]$containerName
    )
    
    $containerExists = docker ps -a --format "{{.Names}}" | Select-String "^$containerName$"
    
    if ($containerExists) {
        Write-Host "Stopping and removing container: $containerName"
        docker stop $containerName
        docker rm $containerName
    }
}

# Remove existing containers
Remove-ContainerIfExists -containerName "zookeeper"
Remove-ContainerIfExists -containerName "kafka"

# Check if the network exists and remove it if necessary
$networkExists = docker network ls | Select-String "kafka-net"

# If network exists - delete it
if ($networkExists) {
    Write-Host "Removing Network kafka-net"
    docker network rm kafka-net
}

# Create the network
docker network create kafka-net

# Run Zookeeper container
docker run -d --name zookeeper --network kafka-net -p 2181:2181 `
  -e ZOOKEEPER_CLIENT_PORT=2181 `
  confluentinc/cp-zookeeper:latest

# Run Kafka container
docker run -d --name kafka --network kafka-net -p 9092:9092 `
  -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 `
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 `
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 `
  confluentinc/cp-kafka:latest
