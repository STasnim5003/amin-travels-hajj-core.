#!/bin/bash

sudo su

echo "==> Stopping containers..."
docker compose down

echo "==> Pulling latest code from dev..."
git pull origin dev



echo "==> Building and starting containers..."
docker compose up -d --build

echo "==> Deployment completed successfully!"