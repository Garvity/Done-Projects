#!/bin/bash
set -e

APP_NAME="flaskapp"
DOCKER_IMAGE="yourdockerhubusername/flaskapp:latest"

# Stop & remove old container if running
docker rm -f $APP_NAME || true

# Pull latest image
docker pull $DOCKER_IMAGE

# Run new container
docker run -d --name $APP_NAME -p 80:5000 $DOCKER_IMAGE
