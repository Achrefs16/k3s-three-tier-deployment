#!/bin/bash
set -e

FRONTEND_IMAGE="achrefs161/student-frontend:latest"
BACKEND_IMAGE="achrefs161/student-backend:latest"

echo "📦 Building frontend..."
docker build -t $FRONTEND_IMAGE ../app/frontend/

echo "📦 Building backend..."
docker build -t $BACKEND_IMAGE ../app/backend/

echo "🚀 Pushing images to Docker Hub..."
docker push $FRONTEND_IMAGE
docker push $BACKEND_IMAGE

echo "✅ Build & push completed."
