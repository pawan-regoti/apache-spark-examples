# apache-spark-examples

> To read how apache spark works, go to [./documentation/intro.md](./documentation/intro.md)

## To run examples:
- Open Terminal in <repo-root>
- run command `make init` (it will create .venv, and installs poetry)
- run command `make install` (it will install all python dependencies)
- to run a python file
  - run command `make run TARGET=<PATH_TO_PYTHON_FILE>` e.g. `make run TARGET=./src/sample.py`
  - Or, run command `poetry run python PATH_TO_PYTHON_FILE` e.g. `poetry run python ./src/sample.py`
