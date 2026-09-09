# Databricks resources

## Variaveis necessarias

Configure no ambiente do Airflow, em uma Connection/Secret backend ou no `.env` local apenas para desenvolvimento:

```text
DATABRICKS_HOST=https://<workspace>.cloud.databricks.com
DATABRICKS_TOKEN=<token-do-ambiente>
DATABRICKS_VOLUME_PATH=/Volumes/<catalog>/<schema>/<volume>/gold
```

Nunca versione `DATABRICKS_TOKEN`.

## Fluxo

1. A DAG `crypto_databricks_upload` lista os Parquets do bucket Gold no MinIO.
2. Cada objeto e enviado para o mesmo caminho relativo no Volume Unity Catalog.
3. O notebook `load_gold_to_delta.py` le os Parquets do Volume.
4. Cada arquivo e materializado como Delta Table com `overwriteSchema`.
5. A contagem de linhas e impressa para validacao.

A DAG cloud e manual (`schedule=None`) ate que um workspace real, Volume e credencial estejam configurados.
