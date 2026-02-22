#!/bin/bash

echo "Setting up Kubernetes for Spark..."

kubectl create serviceaccount spark --namespace=default

kubectl create clusterrolebinding spark-role \
    --clusterrole=edit \
    --serviceaccount=default:spark \
    --namespace=default

echo "✅ Kubernetes setup complete!"
echo ""
echo "Verify with:"
echo "  kubectl auth can-i create pods --as=system:serviceaccount:default:spark"
