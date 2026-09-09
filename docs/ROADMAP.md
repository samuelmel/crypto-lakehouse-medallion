# Roadmap - Crypto Lakehouse

Roadmap do projeto de portfólio de Data Lakehouse de criptomoedas. Cada fase só deve ser encerrada depois que o critério de conclusão for validado.

## Status atual

- [x] Fase 1 - Infraestrutura local Docker
- [x] Fase 2 - Ingestão Bronze com Python e CoinGecko
- [x] Fase 3 - Configuração dbt + DuckDB + MinIO
- [x] Fase 4 - Transformação Silver
- [x] Fase 5 - Modelagem Gold e Star Schema
- [x] Fase 6 - Orquestração ponta a ponta
- [ ] Fase 7 - Integração Databricks
- [ ] Fase 8 - Governança e otimização cloud
- [ ] Fase 9 - Power BI
- [ ] Fase 10 - Documentação e portfólio

## Fase 1 - Infraestrutura local

### Objetivo

Disponibilizar uma base local reproduzível para o Lakehouse.

### Entregáveis

- Docker Compose funcional.
- PostgreSQL para metadados do Airflow.
- MinIO com buckets `bronze`, `silver` e `gold`.
- Airflow com webserver, scheduler e `airflow-init`.
- Imagem customizada com `uv`, dbt, DuckDB e bibliotecas Python.
- Variáveis externas em `.env`.
- Health checks e volumes persistentes.

### Critério de conclusão

- `docker compose up -d` executa sem erro.
- PostgreSQL aparece como saudável.
- MinIO responde em `http://localhost:9000`.
- Os três buckets existem.
- Airflow responde em `http://localhost:8080/health` com HTTP 200.
- Nenhum segredo está versionado.

## Fase 2 - Ingestão Bronze

### Objetivo

Consumir a CoinGecko e preservar o payload bruto no MinIO sem duplicação.

### Entregáveis

- Cliente Python para a API.
- Configuração de ativos e endpoints por variável de ambiente.
- Timeout, retries e tratamento de erros HTTP.
- Upload para o bucket `bronze`.
- Chave determinística por ativo, endpoint e data de referência.
- Metadados de ingestão, como timestamp e fonte.
- DAG Airflow para disparar a ingestão.
- Testes unitários com cliente HTTP e storage simulados.

### Critério de conclusão

- Uma execução grava um JSON válido no Bronze.
- Dez execuções no mesmo período não duplicam o objeto lógico.
- Falhas de API aparecem nos logs e produzem retry controlado.
- A DAG pode ser executada pela interface do Airflow.
- O teste automatizado comprova a idempotência.

### Resultado validado

- DAG `crypto_bronze_ingestion` carregada sem erros.
- Execução manual concluída com estado `success`.
- Objeto JSON confirmado no bucket `bronze`.
- Testes unitários de idempotência aprovados.

## Fase 3 - dbt, DuckDB e acesso ao MinIO

### Objetivo

Preparar o motor de transformação para ler e escrever objetos no armazenamento S3 compatível.

### Entregáveis

- Projeto dbt validado com `dbt debug`.
- Adapter `dbt-duckdb` funcionando.
- Extensão `httpfs`/configuração S3 documentada.
- Credenciais do MinIO fora do código.
- Modelo de leitura dos arquivos Bronze.
- Comando executável pelo Airflow.

### Critério de conclusão

- `dbt debug` passa.
- DuckDB lê um objeto de teste do MinIO.
- Um modelo dbt executa do início ao fim.
- A configuração funciona após reiniciar os containers.

### Resultado validado

- dbt 1.12.4 e `dbt-duckdb` 1.11.0 carregados no Airflow.
- `dbt debug` concluído com `All checks passed!`.
- Extensão DuckDB `httpfs` conectada ao MinIO via endpoint S3 compatível.
- Modelo `stg_bronze_market` executado com `PASS=1`.
- JSON Bronze lido e materializado como tabela DuckDB.

## Fase 4 - Camada Silver

### Objetivo

Transformar JSONs brutos em dados limpos, tipados e persistidos em Parquet.

### Entregáveis

- Modelos staging.
- Flattening de arrays e objetos aninhados.
- Tipagem de datas, preços, volumes e identificadores.
- Regras para nulos e registros inválidos.
- Escrita no bucket `silver` em Parquet.
- Documentação de schema e granularidade.
- Testes dbt básicos.

### Critério de conclusão

- O Parquet Silver possui schema estável.
- Não existem identificadores obrigatórios nulos.
- As colunas de preço e data têm tipos corretos.
- Os testes `not_null` e `unique` passam.
- Reprocessar a mesma Bronze não duplica registros Silver.

### Resultado validado

- Modelo `silver_market_prices` criado com flattening via `json_each`.
- Preços, market cap, volume e variação tipados com `try_cast`.
- Parquet gravado em `s3://silver/market/silver_market_prices.parquet`.
- Cinco testes dbt aprovados: `unique` e `not_null`.
- `dbt show` confirmou registros de Bitcoin e Ethereum.
- Segunda execução regravou o mesmo destino sem criar arquivo adicional.

## Fase 5 - Camada Gold e Star Schema

### Objetivo

Criar o modelo dimensional pronto para análise.

### Entregáveis

- `dim_cryptos`.
- `dim_calendario`.
- `fact_precos_mercado`.
- `agg_volatilidade_diaria`.
- Definição de granularidade, PKs e FKs.
- Parquets no bucket `gold`.
- Testes `unique`, `not_null` e `relationships`.
- Diagrama ERD atualizado no dbdiagram.io.

### Critério de conclusão

- Cada modelo executa com `dbt build`.
- Chaves são únicas e não nulas.
- Relacionamentos entre fatos e dimensões são válidos.
- As métricas de volatilidade são reproduzíveis.
- O modelo responde às perguntas analíticas definidas.

### Resultado validado

- `dim_cryptos`, `dim_calendario`, `fact_precos_mercado` e `agg_volatilidade_diaria` criados.
- Quatro Parquets Gold confirmados no MinIO.
- `dbt build --select marts+` concluído com `PASS=26`, `WARN=0` e `ERROR=0`.
- Testes `unique`, `not_null` e `relationships` aprovados.
- Chaves de data e ativo conectam fatos às dimensões.
- `dim_cryptos` usa o `crypto_id` como nome técnico até uma futura ingestão de metadados oficiais.

## Fase 6 - Orquestração ponta a ponta

### Objetivo

Automatizar Bronze, Silver e Gold em uma DAG observável e reexecutável.

### Entregáveis

- DAG com dependências explícitas.
- Retries, timeouts e logs.
- Execução incremental por data.
- Reprocessamento controlado.
- Connections e Variables do Airflow.
- Alertas ou notificação de falha.
- Teste de execução completa.

### Critério de conclusão

- Uma DAG executa o fluxo completo.
- Uma falha em uma etapa não corrompe as camadas anteriores.
- A reexecução é idempotente.
- Os logs permitem localizar a causa de uma falha.

### Resultado validado

- DAG `crypto_lakehouse_pipeline` criada com dependências explícitas.
- Fluxo executado com sucesso: Bronze -> Silver -> testes Silver -> Gold.
- Todas as quatro tarefas terminaram em `success`.
- `DagRun` manual concluído em aproximadamente 37 segundos.
- Retries e timeouts definidos por tarefa.
- `max_active_runs=1` evita execuções concorrentes do pipeline.

## Fase 7 - Integração com Databricks

### Objetivo

Enviar a camada Gold para a nuvem e convertê-la em Delta Tables.

### Entregáveis

- Autenticação segura com Databricks.
- Upload dos Parquets Gold.
- Organização em Volumes.
- Notebooks PySpark.
- Conversão Parquet para Delta.
- Catálogo, schema e tabelas definidos.
- Validação de contagem e schema pós-carga.

### Critério de conclusão

- Os arquivos chegam ao destino correto.
- As Delta Tables são criadas sem perda de registros.
- Schema local e cloud são comparados.
- O processo pode ser repetido sem duplicação.

### Preparação local validada

- Uploader MinIO -> Databricks criado em `src/databricks/upload_gold.py`.
- Upload filtra somente Parquets e substitui o mesmo caminho em reexecuções.
- Testes locais do uploader aprovados com storage e HTTP simulados.
- DAG manual `crypto_databricks_upload` carregada no Airflow sem erros de importação.
- Notebook `databricks/notebooks/load_gold_to_delta.py` criado para Parquet -> Delta.
- Configuração documentada em `databricks/resources/README.md`.

### Bloqueio para validação cloud

- Ainda falta um workspace Databricks real, Unity Catalog, Volume e token configurados.
- A execução da DAG cloud e do notebook deve ocorrer somente após configurar `DATABRICKS_HOST`, `DATABRICKS_TOKEN` e `DATABRICKS_VOLUME_PATH` por secret backend ou ambiente seguro.

## Fase 8 - Governança e otimização cloud

### Objetivo

Aplicar práticas de governança, segurança e performance.

### Entregáveis

- Unity Catalog configurado.
- Permissões mínimas necessárias.
- PKs e FKs documentadas ou aplicadas conforme suporte do ambiente.
- Liquid Clustering ou estratégia de otimização validada.
- Retenção e qualidade documentadas.
- Separação entre desenvolvimento e produção.

### Critério de conclusão

- Acesso é concedido por princípio do menor privilégio.
- Consultas principais têm performance medida.
- Custos e limitações da configuração estão documentados.

## Fase 9 - Power BI

### Objetivo

Disponibilizar o modelo Gold para consumo analítico.

### Entregáveis

- Conexão DirectQuery ou modo aprovado para o destino.
- Relacionamentos do modelo semântico.
- Medidas de preço, volume e volatilidade.
- Dashboard de evolução e comparação de criptoativos.
- Validação dos números contra as Delta Tables.

### Critério de conclusão

- O relatório atualiza sem erro.
- As métricas conferem com consultas de validação.
- O usuário consegue analisar preço, volume e volatilidade por período e ativo.

## Fase 10 - Documentação e portfólio

### Objetivo

Transformar o projeto em uma apresentação técnica reproduzível.

### Entregáveis

- README com setup e troubleshooting.
- Diagrama PlantUML da arquitetura.
- Diagrama ERD no dbdiagram.io.
- Decisões arquiteturais registradas.
- Evidências de testes.
- Exemplo de execução bem-sucedida.
- Limitações conhecidas.
- Roadmap e próximos passos.

### Critério de conclusão

- Uma pessoa consegue entender a arquitetura pelo README.
- Uma pessoa consegue reproduzir o ambiente sem acessar segredos.
- O projeto diferencia claramente ambiente local, cloud e planejamento futuro.

## Regras de trabalho

- Não avançar de fase sem validar o critério de conclusão.
- Não versionar `.env`, tokens, senhas ou chaves.
- Manter ingestão e transformações idempotentes.
- Preferir testes pequenos antes de testes ponta a ponta.
- Registrar decisões e limitações quando uma tecnologia tiver comportamento dependente de versão.
- Atualizar este roadmap ao concluir cada entrega relevante.
