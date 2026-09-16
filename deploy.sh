#!/bin/bash

set -e

echo "==> Pulling latest code from dev..."
git pull origin dev

echo "==> Stopping containers..."
sudo docker compose down

echo "==> Building and starting containers..."
sudo docker compose up -d --build

echo "==> Deployment completed successfully!"