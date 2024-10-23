#!/bin/bash

# Variables
IMAGE_NAME="fbl-app-api"
CONTAINER_NAME="fbl-app-api-container"
HOST_PORT=8007
CONTAINER_PORT=8007
DOCKER_NETWORK="my_network"

echo "Building Docker image..."
docker build -t $IMAGE_NAME .

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Remove existing container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

echo "Running container..."
docker run -d --name $CONTAINER_NAME --network $DOCKER_NETWORK -p $HOST_PORT:$CONTAINER_PORT $IMAGE_NAME

echo "Logs:"
docker logs -f $CONTAINER_NAME
