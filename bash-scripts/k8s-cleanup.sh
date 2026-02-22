#!/bin/bash

echo "Cleaning up Spark job resources..."

echo "Deleting Spark pods..."
kubectl delete pods -l spark-role=driver --namespace=default 2>/dev/null || true
kubectl delete pods -l spark-role=executor --namespace=default 2>/dev/null || true

echo "Deleting completed/failed pods..."
kubectl delete pods --field-selector=status.phase=Succeeded --namespace=default 2>/dev/null || true
kubectl delete pods --field-selector=status.phase=Failed --namespace=default 2>/dev/null || true

echo "Deleting Spark services..."
kubectl delete services -l spark-role=driver --namespace=default 2>/dev/null || true

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Service account and permissions remain intact for next run."
echo "To completely remove everything, run: make local-k8s-teardown"
