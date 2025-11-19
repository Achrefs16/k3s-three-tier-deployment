#!/bin/bash
set -e

NAMESPACE="student-app"
K8S_DIR="../k8s"

echo "🚀 Deploying application stack to K3s..."
echo "---------------------------------------"

echo "📁 Creating namespace (if not exists)..."
kubectl apply -f $K8S_DIR/namespace.yaml

echo "🔐 Applying ConfigMap and Secret..."
kubectl apply -f $K8S_DIR/backend-configmap.yaml
kubectl apply -f $K8S_DIR/db-secret.yaml

echo "🐘 Deploying PostgreSQL (StatefulSet + Services)..."
kubectl apply -f $K8S_DIR/postgres-headless-service.yaml
kubectl apply -f $K8S_DIR/postgres-service.yaml
kubectl apply -f $K8S_DIR/postgres-statefulset.yaml

echo "⏳ Waiting for PostgreSQL pod to be ready..."
kubectl wait --for=condition=ready pod/postgres-0 -n $NAMESPACE --timeout=180s

echo "🖥 Deploying backend..."
kubectl apply -f $K8S_DIR/backend-deployment.yaml
kubectl apply -f $K8S_DIR/backend-service.yaml

echo "🌐 Deploying frontend..."
kubectl apply -f $K8S_DIR/frontend-deployment.yaml
kubectl apply -f $K8S_DIR/frontend-service.yaml

echo "⏳ Waiting for backend to be ready..."
kubectl rollout status deployment/backend -n $NAMESPACE

echo "⏳ Waiting for frontend to be ready..."
kubectl rollout status deployment/frontend -n $NAMESPACE

echo "📊 Deployment Summary:"
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE
kubectl get pvc -n $NAMESPACE

echo "✅ Deployment completed successfully!"
