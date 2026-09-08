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
├── .env.example             # Variáveis locais (copiar para .env)
└── docker-compose.yml       # Infraestrutura local
```

## Próximo passo

Copie `.env.example` para `.env` e valide a infraestrutura com:

```bash
docker compose up -d --build
```

Interfaces locais:

- Airflow: http://localhost:8080
- MinIO Console: http://localhost:9001
