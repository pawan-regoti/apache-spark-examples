# apache-spark-examples

> To read how apache spark works, go to [./documentation/intro.md](./documentation/intro.md)

## To run examples:
- Open Terminal in <repo-root>
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

