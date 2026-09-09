# Roadmap - Crypto Lakehouse

Roadmap do projeto de portfólio de Data Lakehouse de criptomoedas. Cada fase só deve ser encerrada depois que o critério de conclusão for validado.

## Status atual

- [x] Fase 1 - Infraestrutura local Docker
- [ ] Fase 2 - Ingestão Bronze com Python e CoinGecko
- [ ] Fase 3 - Configuração dbt + DuckDB + MinIO
- [ ] Fase 4 - Transformação Silver
- [ ] Fase 5 - Modelagem Gold e Star Schema
- [ ] Fase 6 - Orquestração ponta a ponta
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
