# Crypto Lakehouse

Data Lakehouse de criptomoedas com arquitetura Medalhão.

## Stack

- Docker Compose
- MinIO: armazenamento S3 local
- Apache Airflow: orquestração
- DuckDB + dbt: transformação
- Databricks: destino Delta Lake
- Power BI: consumo analítico

## Estrutura

```text
.
├── airflow/                 # DAGs, logs e plugins
├── dbt/                     # Projeto dbt e modelos Silver/Gold
├── databricks/              # Notebooks e recursos de implantação
├── docker/airflow/          # Imagem do Airflow com dependências
├── src/ingestion/           # Clientes de API e ingestão Bronze
├── tests/                   # Testes automatizados
├── docs/ROADMAP.md          # Fases, entregáveis e critérios de conclusão
├── .env.example             # Variáveis locais (copiar para .env)
└── docker-compose.yml       # Infraestrutura local
```

## Roadmap

Consulte o [roadmap do projeto](docs/ROADMAP.md) para acompanhar as fases, entregáveis e critérios de validação.

## Diagramas do projeto

### Arquitetura e fluxo de ingestão

![Arquitetura e fluxo de ingestão do Crypto Lakehouse](img/CoinGecko%20API%20Ingestion-2026-09-09-001131.png)

### Estrutura analítica do banco

![Estrutura analítica do banco de dados](img/Untitled.png)

## Próximo passo

Copie `.env.example` para `.env` e valide a infraestrutura com:

```bash
docker compose up -d --build
```

## Ambiente Python local

O ambiente local usa `uv` para instalar as bibliotecas de desenvolvimento e testes:

```bash
uv sync
uv run python -m unittest tests.test_coingecko_bronze tests.test_databricks_upload -v
uv run dbt --version
```

O Airflow e as DAGs são executados dentro dos containers Docker. O `pyproject.toml` não instala Airflow localmente; isso evita duplicar a infraestrutura e mantém o runtime igual ao ambiente orquestrado.

Interfaces locais:

- Airflow: http://localhost:8080
- MinIO Console: http://localhost:9001
