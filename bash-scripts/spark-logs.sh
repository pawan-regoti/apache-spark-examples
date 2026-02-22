#!/bin/bash

echo "Retrieving Spark job logs..."
echo ""

# Find all Spark driver pods (including completed)
DRIVER_PODS=$(kubectl get pods -n default -l spark-role=driver -o jsonpath='{.items[*].metadata.name}')

if [ -z "$DRIVER_PODS" ]; then
    echo "❌ No Spark driver pods found."
    echo "Run a job first: make local-k8s-submit"
    exit 1
fi

echo "Available Spark driver pods:"
echo "----------------------------"
kubectl get pods -n default -l spark-role=driver
echo ""

# Get the most recent driver pod
LATEST_DRIVER=$(kubectl get pods -n default -l spark-role=driver --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

echo "Showing logs from: $LATEST_DRIVER"
echo "================================"
echo ""

kubectl logs -n default $LATEST_DRIVER --tail=100

echo ""
echo "----------------------------"
echo "To view logs from a specific pod:"
echo "  kubectl logs -n default <pod-name>"
echo ""
echo "To view all logs (no tail limit):"
echo "  kubectl logs -n default $LATEST_DRIVER"
echo ""
echo "To follow logs in real-time:"
echo "  kubectl logs -n default $LATEST_DRIVER -f"
