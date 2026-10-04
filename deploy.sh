#!/bin/bash

set -e

echo "==> Pulling latest code from dev..."
git pull origin dev

echo "==> Saving audit log lines before the container (and its logs) is replaced..."
mkdir -p ../logs
docker logs amin-travels-hajj-dev 2>&1 | grep "AUDIT " >> ../logs/pilgrim_audit.log || true

echo "==> Stopping containers..."
docker compose down

echo "==> Removing old backend container if it exists..."
docker rm -f amin-travels-hajj-dev 2>/dev/null || true

echo "==> Building and starting containers..."
docker compose up -d --build

echo "==> Deployment completed successfully!"