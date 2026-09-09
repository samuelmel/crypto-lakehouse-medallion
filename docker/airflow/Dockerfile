FROM apache/airflow:2.10.4-python3.12

COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /bin/
COPY docker/airflow/requirements.txt /requirements.txt

USER root
RUN apt-get update \
	&& apt-get install -y --no-install-recommends git \
	&& rm -rf /var/lib/apt/lists/*
RUN uv pip install --system --no-cache -r /requirements.txt

USER airflow
RUN pip install --target /home/airflow/.local/lib/python3.12/site-packages \
	--upgrade --no-cache-dir \
	"typing-extensions>=4.15.0,<5" "protobuf>=5.26.0,<7"
