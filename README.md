# Crypto Lakehouse 🚀

Data Lakehouse de criptomoedas construído com **Arquitetura Medalhão (Bronze, Silver, Gold)**, processando dados de mercado de alta frequência de forma totalmente automatizada, limpa, testada e pronta para análises avançadas.

---

## 🏗 Arquitetura do Lakehouse

O pipeline foi projetado seguindo as melhores práticas da Engenharia de Dados moderna:

- **Bronze (Raw Data)**: Ingestão orientada a eventos/snapshots dos dados brutos da API CoinGecko salvos como arquivos JSON no MinIO (S3 compatível) com chaveamento determinístico e idempotência.
- **Silver (Cleaned & Standardized)**: Desaninhamento (flattening), tipagem estrita de preços, volumes e timestamps, armazenados em formato Parquet via **dbt + DuckDB**.
- **Gold (Analytical / Star Schema)**: Modelagem dimensional (Tabelas Fato e Dimensão + Agregações de Volatilidade Diária) prontas para consumo de dados e alta performance analítica.
- **Databricks Cloud / Delta Lake**: Automação de upload dos Parquets da camada Gold para o Databricks Unity Catalog / Volumes com conversão em **Delta Tables** via PySpark.

---

## 🛠 Stack Tecnológica

| Componente | Tecnologia | Função |
| :--- | :--- | :--- |
| **Infraestrutura** | Docker Compose | Conteinerização do ambiente local |
| **Storage (S3 Local)** | MinIO | Armazenamento de objetos (Buckets Bronze, Silver, Gold) |
| **Orquestração** | Apache Airflow | DAGs de ingestão, transformações e carga cloud |
| **Transformação** | dbt + DuckDB | Modelagem SQL, tratamento e data quality |
| **Cloud / Delta Lake** | Databricks + PySpark | Destino final dos dados em formato Delta Lake |
| **Testes & Gerenciador** | Python (`uv`, `unittest`) | Scripting, testes automatizados e gestão de pacotes |

---

## 📁 Estrutura do Projeto

```text
.
├── airflow/                 # DAGs de orquestração (Ingestão, Pipeline e Cloud Upload)
├── dbt/                     # Projeto dbt, macros, modelos (Staging, Silver e Gold Star Schema)
├── databricks/              # Notebooks PySpark para conversão Parquet -> Delta Lake
├── docker/airflow/          # Dockerfile e dependências customizadas do Airflow
├── src/
│   ├── ingestion/           # Cliente HTTP e ingestão idempotente para a camada Bronze
│   └── databricks/          # Script de upload automatizado Gold -> Databricks Volume
├── tests/                   # Suíte de testes unitários automatizados (mocks de S3 e HTTP)
├── docs/ROADMAP.md          # Fases do projeto, critérios de aceite e resultados validados
├── .env.example             # Template de variáveis de ambiente
└── docker-compose.yml       # Orquestração da infraestrutura local
```

---

## 📊 Diagramas de Arquitetura

### 1. Arquitetura de Ingestão e Pipeline
![Arquitetura e fluxo de ingestão do Crypto Lakehouse](img/CoinGecko%20API%20Ingestion-2026-09-09-001131.png)

### 2. Estrutura Analítica (Star Schema)
![Estrutura analítica do banco de dados](img/Untitled.png)

---

## 📊 Resultados e Queries de Exemplo

O pipeline processa dados de mercado de criptomoedas em três camadas. Abaixo estão consultas ilustrativas para explorar os dados:

### Silver - Preços limpos e tipados
```sql
-- Últimas observações de Bitcoin e Ethereum
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
```

### Gold - Fato de preços de mercado
```sql
-- Séries históricas de preços por ativo
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
```

### Gold - Volatilidade diária
```sql
-- Volatilidade e retorno diário por ativo
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

## 🚀 Como Executar Localmente

### 1. Primeiros Passos
```bash
# Instale as dependências
docker compose up -d --build

# Crie .env com as variáveis do .env.example
cp .env.example .env
```

### 2. Execução local do dbt (recomendada para desenvolvimento)
Este método funciona tanto dentro quanto fora do Docker. Ele usa um DuckDB local em vez de ficar restrito a `/opt/airflow/dbt`.

```bash
# Sincronize o ambiente de desenvolvimento local
uv sync

# Configure o perfil local do dbt (.dbt/profiles.yml)
mkdir -p ~/.dbt
cp dbt/profiles.yml ~/.dbt/

# Execute o dbt debug para validar
uv run dbt debug --profiles-dir ~/.dbt

# Execute os modelos
uv run dbt run --select stg_bronze_market --profiles-dir ~/.dbt
uv run dbt run --select silver_market_prices --profiles-dir ~/.dbt
uv run dbt build --select +marts --profiles-dir ~/.dbt
```

### 3. Execução dentro do Docker Airflow (pipeline completa)
```bash
# As subidas do Docker já configuram as dependências
# Execute a pipeline completa
uv run python -m unittest tests.test_coingecko_bronze tests.test_databricks_upload -v
```

Interfaces disponíveis após a subida dos containers:
- **Airflow Webserver**: [http://localhost:8080](http://localhost:8080) (user: `admin` / pass: `admin`)
- **MinIO Console**: [http://localhost:9001](http://localhost:9001) (user: `minioadmin` / pass: `minioadmin`)

---

## 📋 Roadmap & Critérios de Aceite
Para detalhes sobre cada fase de desenvolvimento, entregáveis e validações concluídas, consulte o [Roadmap do Projeto](docs/ROADMAP.md).

