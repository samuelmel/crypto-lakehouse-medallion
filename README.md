# Crypto Lakehouse 
### *Data Lakehouse de Criptomoedas com Arquitetura Medalhão (Bronze, Silver, Gold)*

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![dbt](https://img.shields.io/badge/dbt-core-1.8%2B-brightgreen.svg)](https://www.getdbt.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.1%2B-orange.svg)](https://duckdb.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Apache Airflow](https://img.shields.io/badge/Airflow-2.10%2B-017CEE.svg)](https://airflow.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Data Lakehouse de criptomoedas construído com Arquitetura Medalhão, processando dados de mercado de alta frequência de forma totalmente automatizada, limpa, testada e pronta para análises avançadas.**

---

## 🌟 Principais Funcionalidades

1. **Arquitetura Medalhão Completa (Bronze → Silver → Gold)**
   - **Bronze**: Ingestão idempotente de dados brutos da API CoinGecko no MinIO (S3 compatível) com chaveamento determinístico
   - **Silver**: Desaninhamento (flattening), tipagem estrita e armazenamento em Parquet via dbt + DuckDB
   - **Gold**: Modelagem dimensional (Star Schema) com tabelas de fatos, dimensões e agregações de volatilidade diária

2. **Orquestração com Apache Airflow**
   - DAGs para ingestão Bronze, pipeline Silver-Gold e upload para Databricks
   - Retries configuráveis, timeouts, logs detalhados e controle de execução concorrente
   - Interface web para monitoramento e disparo manual de pipelines

3. **Transformação com dbt + DuckDB**
   - Modelos SQL testados com validações de integridade (not_null, unique, relationships)
   - Suporte nativo à leitura direta de S3 via extensão `httpfs` do DuckDB
   - Materialização externa (Parquet) nas camadas Silver e Gold para máxima performance

4. **Integração Cloud com Databricks**
   - Upload automático de Parquets Gold para Unity Catalog / Volumes
   - Notebook PySpark para conversão eficiente em Delta Tables
   - Preparado para ambientes de produção com governance e segurança

5. **Testes Automatizados Abrangentes**
   - Testes unitários com mocks de S3 e HTTP usando `unittest`
   - Testes dbt de qualidade de dados em cada camada
   - Validação de idempotência e reprocessamento controlado

---

## 📌 Por que usar?

* **Stack Moderna e Popular**: Docker, Airflow, dbt, DuckDB, MinIO, Databricks - tecnologias amplamente adotadas no mercado
* **Reprodutibilidade Total**: Ambiente completamente definido em `docker-compose.yml` e `.env.example`
* **Qualidade de Dados Garantida**: Testes de unicidade, não-nulidade e relacionamentos em cada etapa do pipeline
* **Escalabilidade Pronta para Produção**: Camada Gold estruturada para consumo direto em ferramentas de BI, ML ou data science
* **Documentação Exemplar**: Arquitetura detalhada, roadmap com critérios de aceite, queries práticas e guia de execução
* **Foco em Boas Práticas**: Código limpo, separação de preocupações, idempotência e tratamento de erros robusto

---

## ⚡ Quickstart

### 1. Instalação das Dependências

Recomendamos o uso do [`uv`](https://github.com/astral-sh/uv) pela velocidade, mas `pip` também funciona.

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/crypto-lakehouse.git
cd crypto-lakehouse

# Usando uv (recomendado):
uv venv
source .venv/bin/activate      # No Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Ou usando pip tradicional:
python -m venv .venv
source .venv/bin/activate      # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Subir a Infraestrutura Local

```bash
# Copie o template de variáveis de ambiente
cp .env.example .env

# Suba todos os containers (MinIO, PostgreSQL, Airflow, etc.)
docker compose up -d --build
```

Após a subida, acesse as interfaces:
- **Airflow Webserver**: http://localhost:8080 (usuário: `admin` / senha: `admin`)
- **MinIO Console**: http://localhost:9001 (usuário: `minioadmin` / senha: `minioadmin`)

### 3. Executar o dbt Localmente (ideal para desenvolvimento e testes)

```bash
# Sincronize o ambiente de desenvolvimento
uv sync

# Configure o perfil local do dbt (copie para ~/.dbt ou use o diretório do projeto)
mkdir -p ~/.dbt
cp dbt/profiles.yml ~/.dbt/

# Valide a conexão e configuração
uv run dbt debug --profiles-dir ~/.dbt

# Execute os modelos por camada
uv run dbt run --select stg_bronze_market --profiles-dir ~/.dbt          # Staging (Bronze)
uv run dbt run --select silver_market_prices --profiles-dir ~/.dbt      # Silver
uv run dbt build --select +marts --profiles-dir ~/.dbt                  # Gold (Star Schema completo)
```

### 4. Executar Testes e Pipeline Completa

```bash
# Rode a suíte de testes unitários (valida ingestão e upload para Databricks)
uv run python -m unittest tests.test_coingecko_bronze tests.test_databricks_upload -v

# Ou execute a pipeline completa via Airflow UI em http://localhost:8080
```

---

## 💻 Exemplo de Código Gerado (SQL dbt)

Abaixo está o modelo Silver (`silver_market_prices.sql`) que demonstra o processamento de dados brutos da CoinGecko:

```sql
{{ config(
    materialized='external',
    location='s3://silver/market/silver_market_prices.parquet',
    format='parquet'
) }}

with bronze_snapshots as (
    select
        source,
        endpoint,
        reference_date::date as reference_date,
        ingested_at::timestamp as ingested_at,
        vs_currency,
        data
    from {{ ref('stg_bronze_market') }}
),
flattened_market as (
    select
        md5(
            concat(
                reference_date::varchar,
                ':',
                asset.key,
                ':',
                vs_currency
            )
        ) as market_record_id,
        asset.key as crypto_id,
        reference_date,
        ingested_at,
        vs_currency,
        try_cast(json_extract_string(asset.value, '$.usd') as decimal(38, 8)) as price_usd,
        try_cast(json_extract_string(asset.value, '$.usd_market_cap') as decimal(38, 8)) as market_cap_usd,
        try_cast(json_extract_string(asset.value, '$.usd_24h_vol') as decimal(38, 8)) as total_volume_usd,
        try_cast(json_extract_string(asset.value, '$.usd_24h_change') as decimal(18, 8)) as price_change_24h,
        try_cast(json_extract_string(asset.value, '$.last_updated_at') as bigint) as source_updated_at,
        source,
        endpoint
    from bronze_snapshots,
    lateral json_each(to_json(data)) as asset
)

select *
from flattened_market
where crypto_id is not null
  and reference_date is not null
```

### Consultas de Exemplo para Exploração

```sql
-- Silver: Últimas observações de preço e volume
SELECT
    crypto_id,
    reference_date,
    price_usd,
    market_cap_usd,
    total_volume_usd,
    price_change_24h
FROM silver_market_prices
ORDER BY reference_date DESC, ingested_at DESC
LIMIT 10;

-- Gold: Série histórica de preços com símbolos legíveis
SELECT
    d.symbol,
    f.reference_date,
    f.price_usd,
    f.market_cap_usd,
    f.total_volume_usd
FROM fact_precos_mercado f
JOIN dim_cryptos d USING (crypto_id)
ORDER BY f.reference_date DESC
LIMIT 20;

-- Gold: Análise de volatilidade e retorno diário
SELECT
    d.symbol,
    v.reference_date,
    v.opening_price_usd,
    v.closing_price_usd,
    v.daily_return,
    v.volatility
FROM agg_volatilidade_diaria v
JOIN dim_cryptos d USING (crypto_id)
ORDER BY v.reference_date DESC, v.volatility DESC;
```

---

## 🛠️ Conectores & Tecnologias Suportadas

| Categoria | Tecnologia | Detalhes |
|-----------|------------|----------|
| **Orquestração** | Apache Airflow 2.10+ | DAGs com trigger rules, pools e concurrency control |
| **Storage (S3 Local)** | MinIO | API S3 compatível, buckets separados por camada (Bronze/Silver/Gold) |
| **Transformação** | dbt-core + dbt-duckdb + DuckDB 1.1+ | Modelos SQL, testes de integridade, materialização Parquet |
| **Lakehouse Cloud** | Databricks Unity Catalog | Volumes gerenciados, Delta Tables, notebooks PySpark |
| **Ingestão de Dados** | Python + requests | Cliente CoinGecko com retry exponencial e tratamento de rate limits |
| **Orquestração de Containers** | Docker Compose | PostgreSQL (metadata Airflow), MinIO, Airflow (webserver/scheduler/init) |
| **Gerenciamento de Pacotes** | uv / pip | Ambientes isolados, resolução rápida de dependências |
| **Análise Adicional** | Pandas/PyArrow (opcional) | Para exploração interativa em notebooks Jupyter |

---

## 🧪 Executando os Testes Automatizados

### Testes de Unidade (Python)
Valida os componentes de ingestão CoinGecko e upload para Databricks com mocks de S3 e HTTP:

```bash
uv run python -m unittest tests.test_coingecko_bronze tests.test_databricks_upload -v
```

### Testes dbt (Qualidade de Dados)
Verifica integridade, unicidade e relacionamentos em todos os modelos:

```bash
uv run dbt test --profiles-dir dbt/
```

### Build Completo
Executa todos os modelos e testes em sequência:

```bash
uv run dbt build --profiles-dir dbt/
```

---

## 👨‍💻 Autor

**Samuel Santos**

Engenheiro de Dados apaixonado por arquiteturas modernas de dados, automação e boas práticas de engenharia de software. Este projeto foi desenvolvido como portfólio técnico e exercício de estudo, explorando conceitos avançados de:

- Arquitetura Medalhão e Lakehouses
- ELT com dbt e ferramentas open-source
- Orquestração de workflows com Apache Airflow
- Integração entre data lakes locais e plataformas cloud (Databricks)
- Testabilidade e qualidade de dados em pipelines de engenharia

> 🇧🇷 Português | [🇺🇸 English](README_EN.md)