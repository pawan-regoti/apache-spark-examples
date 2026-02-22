.PHONY: init
init:
	rm -rf .venv && \
	python -m venv .venv && \
	. .venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt && \
	make install

.PHONY: install
install:
	poetry install

.PHONY: test
test:
	poetry run pytest -vv test/

.PHONY: run
run:
	poetry run python $(TARGET)

# Docker variables
IMAGE_NAME ?= pyspark-app
IMAGE_TAG ?= latest
REGISTRY ?= localhost:5000

.PHONY: docker-build
docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: docker-tag
docker-tag:
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: docker-push
docker-push: docker-tag
	docker push $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: docker-all
docker-all: docker-build docker-push

.PHONY: check-spark
check-spark:
	@if ! command -v spark-submit &> /dev/null && [ -z "$$SPARK_HOME" ]; then \
		echo "❌ Apache Spark not found!"; \
		echo ""; \
		echo "Install with: brew install apache-spark"; \
		echo "Or download from: https://spark.apache.org/downloads.html"; \
		exit 1; \
	else \
		echo "✅ Apache Spark found"; \
	fi

.PHONY: local-k8s-setup
local-k8s-setup:
	./k8s-setup.sh

.PHONY: local-k8s-submit
local-k8s-submit: check-spark
	make local-k8s-cleanup
	./spark-submit.sh

.PHONY: local-k8s-cleanup
local-k8s-cleanup:
	./k8s-cleanup.sh

.PHONY: local-k8s-teardown
local-k8s-teardown:
	./k8s-teardown.sh

.PHONY: local-k8s-logs
local-k8s-logs:
	@echo "Recent Spark pods:"
	@kubectl get pods -l spark-role --namespace=default
	@echo ""
	@echo "To view logs of a specific pod:"
	@echo "  kubectl logs <pod-name> --namespace=default"

.PHONY: local-k8s-status
local-k8s-status:
	@echo "Spark Pods:"
	@kubectl get pods -l spark-role --namespace=default
	@echo ""
	@echo "Spark Services:"
	@kubectl get services -l spark-role --namespace=default
