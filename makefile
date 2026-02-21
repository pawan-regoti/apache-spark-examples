.PHONY: init
init:
	rm -rf .venv && \
	python -m venv .venv && \
	. .venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt && \

.PHONY: install
install:
	poetry install

.PHONY: test
test:
	poetry run pytest -vv test/
