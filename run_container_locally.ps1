# Define script variables and parameters
param (
    [string]$containerName = "golf-streamlit-frontend",
    [switch]$build
)
$appPortNumber = 8501

# Build docker container locally
if ($build) {
    Write-Host "Building Docker image named '$containerName'..."
    docker build -f frontend\Dockerfile -t $containerName .
    Write-Host "Docker image built `n"
}

# Find containers matching the name
$containers = docker ps -a --filter "name=$containerName" --format "{{.ID}}"

# Stop and remove existing containers
if ($containers) {
    Write-Host "Stopping containers named '$containerName'..."
    docker stop $containers
    Write-Host "Container(s) with ID $containers stopped `n"

    Write-Host "Removing containers named '$containerName'..."
    docker rm $containers
    Write-Host "Container(s) with ID $containers removed `n"
} else {
    Write-Host "No containers named '$containerName' found. `n"
}

# Start up container
Write-Host "Starting container: $containerName..."
docker run -d `
  -p 8501:8501 `
  --env-file "./.env" `
  $containerName
Write-Host "Container started `n"

# Pause to let application spin up
Write-Host "Waiting for application to spin up..."
Start-Sleep -Seconds 3

# Launch App
Start-Process "http://localhost:$appPortNumber"
