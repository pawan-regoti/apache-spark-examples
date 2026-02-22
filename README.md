# apache-spark-examples

> To read how apache spark works, go to [./documentation/intro.md](./documentation/intro.md)

## To run examples:
- Open Terminal in `<repo-root>`
- run command `make init` (it will create .venv, and installs poetry and other dependencies)
- to run a python file
  - run command `make run TARGET=<PATH_TO_PYTHON_FILE>` e.g. `make run TARGET=./src/sample.py`
  - Or, run command `poetry run python PATH_TO_PYTHON_FILE` e.g. `poetry run python ./src/sample.py`

## Running Spark Local Kubernetes cluster like Rancher Desktop
[Running Spark locally](./DEPLOYMENT.md)

## Running Spark on Kubernetes
[Running Spark on Kubernetes](https://spark.apache.org/docs/latest/running-on-kubernetes.html)

## Connect to Spark Connect server
[Launch Spark server with Spark Connect](https://spark.apache.org/docs/4.1.1/api/python/getting_started/quickstart_connect.html#Launch-Spark-server-with-Spark-Connect)

## Command Examples:
`make local-k8s-setup`
![cmd-local-k8s-setup](./documentation/local-k8s-run-example/cmd-local-k8s-setup.png)

---
`make local-k8s-submit`
![cmd-local-k8s-submit](./documentation/local-k8s-run-example/cmd-local-k8s-submit.png)

![rancher-desktop-ui](./documentation/local-k8s-run-example/rancher-desktop-ui.png)

---
`make local-k8s-logs`
![cmd-local-k8s-logs](./documentation/local-k8s-run-example/cmd-local-k8s-logs.png)

---
`make local-k8s-ui`
![cmd-local-k8s-ui](./documentation/local-k8s-run-example/cmd-local-k8s-ui.png)

![spark-ui](./documentation/local-k8s-run-example/spark-ui.png)

![spark-ui-stages](./documentation/local-k8s-run-example/spark-ui-stages.png)

---
`make local-k8s-cleanup`
![cmd-local-k8s-cleanup](./documentation/local-k8s-run-example/cmd-local-k8s-cleanup.png)

---
`make local-k8s-teardown`
![cmd-local-k8s-teardown](./documentation/local-k8s-run-example/cmd-local-k8s-teardown.png)
