#!/bin/bash

# Configuration
# For Rancher Desktop, use: k8s://https://127.0.0.1:6443
K8S_MASTER="k8s://https://127.0.0.1:6443"
IMAGE_NAME="pyspark-app:latest"
APP_NAME="pyspark-sample-example"
EXECUTOR_INSTANCES=5

# Application file (must be inside the Docker image)
APP_FILE="local:///opt/spark/work-dir/src/sample.py"

# Find spark-submit 
# Check common Spark installation locations
SPARK_SUBMIT=""
if [ -n "$SPARK_HOME" ]; then
    SPARK_SUBMIT="$SPARK_HOME/bin/spark-submit"
elif [ -f "/opt/spark/bin/spark-submit" ]; then
    SPARK_SUBMIT="/opt/spark/bin/spark-submit"
elif [ -f "/usr/local/opt/apache-spark/bin/spark-submit" ]; then
    SPARK_SUBMIT="/usr/local/opt/apache-spark/bin/spark-submit"
elif command -v spark-submit &> /dev/null; then
    SPARK_SUBMIT="spark-submit"
else
    echo "Error: spark-submit not found!"
    echo ""
    echo "Please install Apache Spark:"
    echo "  brew install apache-spark"
    echo ""
    echo "Or download from: https://spark.apache.org/downloads.html"
    echo "Then set SPARK_HOME environment variable"
    exit 1
fi

# Submit Spark job to Kubernetes
# Note: Resource settings below are optimized for local Rancher Desktop (minimal CPU requests).
# Current config: 5 executors × 0.1 CPU + 1 driver × 0.1 CPU = 0.6 total CPU cores requested
# For production, increase resources as needed (see DEPLOYMENT.md for guidance)
$SPARK_SUBMIT \
    --master ${K8S_MASTER} \
    --deploy-mode cluster \
    --name ${APP_NAME} \
    --conf spark.executor.instances=${EXECUTOR_INSTANCES} \
    --conf spark.kubernetes.container.image=${IMAGE_NAME} \
    --conf spark.kubernetes.container.image.pullPolicy=Never \
    --conf spark.kubernetes.pyspark.pythonVersion=3 \
    --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
    --conf spark.kubernetes.namespace=default \
    --conf spark.executor.memory=512m \
    --conf spark.driver.memory=512m \
    --conf spark.executor.cores=3 \
    --conf spark.kubernetes.driver.request.cores=0.1 \
    --conf spark.kubernetes.executor.request.cores=0.1 \
    ${APP_FILE}
