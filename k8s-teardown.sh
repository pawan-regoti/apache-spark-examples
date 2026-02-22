#!/bin/bash

echo "⚠️  Complete teardown of Spark Kubernetes resources..."
echo ""
read -p "This will remove service account and permissions. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Teardown cancelled."
    exit 0
fi

echo ""
echo "Cleaning up Spark jobs..."
./k8s-cleanup.sh

echo ""
echo "Removing service account and permissions..."
kubectl delete serviceaccount spark --namespace=default 2>/dev/null || true
kubectl delete clusterrolebinding spark-role 2>/dev/null || true

echo ""
echo "✅ Complete teardown finished!"
echo ""
echo "To setup again, run: make local-k8s-setup"
