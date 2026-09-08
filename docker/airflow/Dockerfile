FROM apache/airflow:2.10.4-python3.12

COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /bin/
COPY docker/airflow/requirements.txt /requirements.txt

USER root
RUN uv pip install --system --no-cache -r /requirements.txt

USER airflow
