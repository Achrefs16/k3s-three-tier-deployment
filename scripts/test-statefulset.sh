#!/bin/bash
set -e

NAMESPACE="student-app"
STATEFULSET="postgres"
SERVICE="postgres-service"

echo "🔍 Checking if StatefulSet exists..."
kubectl get statefulset $STATEFULSET -n $NAMESPACE || { 
    echo "❌ StatefulSet '$STATEFULSET' not found in namespace '$NAMESPACE'."; 
    exit 1; 
}

echo "⏳ Waiting for Pods to be Ready..."
kubectl rollout status statefulset/$STATEFULSET -n $NAMESPACE --timeout=120s

echo "📌 Listing StatefulSet Pods:"
kubectl get pods -l app=$STATEFULSET -n $NAMESPACE -o wide

echo "🧪 Testing connection to PostgreSQL via the Service: $SERVICE"

POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=$STATEFULSET -o jsonpath="{.items[0].metadata.name}")

echo "🔧 Executing psql inside pod: $POD_NAME"

kubectl exec -it $POD_NAME -n $NAMESPACE -- bash -c "psql -U postgres -c '\l'"

echo "✅ PostgreSQL StatefulSet test successful!"
