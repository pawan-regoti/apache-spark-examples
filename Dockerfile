FROM apache/spark:4.0.2-python3

WORKDIR /opt/spark/work-dir

COPY requirements.txt pyproject.toml poetry.lock* ./
ENV HOME=/opt/spark/work-dir

ENV PIP_TARGET=${HOME}/python-deps \
    PATH="${HOME}/python-deps/bin:${PATH}" \
    PYTHONPATH="${HOME}:${HOME}/python-deps" \
    POETRY_HOME=${HOME}/.poetry \
    POETRY_CACHE_DIR=${HOME}/.poetry-cache

RUN pip install --no-cache-dir -r requirements.txt && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction --no-ansi

COPY src/ ./src/

CMD ["/bin/bash"]
