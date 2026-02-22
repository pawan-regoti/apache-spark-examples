#!/bin/bash

echo "Finding Spark driver pod..."
DRIVER_POD=$(kubectl get pods -n default -l spark-role=driver --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$DRIVER_POD" ]; then
    echo "❌ No running Spark driver pod found."
    echo ""
    echo "The Spark UI is only available while the job is running."
    echo "To view historical runs, check the logs:"
    echo "  make local-k8s-logs"
    echo ""
    echo "Or setup Spark History Server (see DEPLOYMENT.md)"
    exit 1
fi

echo "✅ Found driver pod: $DRIVER_POD"
echo ""
echo "Setting up port-forward to Spark UI..."
echo "Spark UI will be available at: http://localhost:4040"
echo ""
echo "Press Ctrl+C to stop port forwarding"
echo ""

kubectl port-forward -n default $DRIVER_POD 4040:4040
