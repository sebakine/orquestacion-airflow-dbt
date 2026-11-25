FROM apache/airflow:3.4.0-python3.12

# dbt va en su propio entorno virtual: sus dependencias chocan con las de Airflow,
# y así cada uno se actualiza por separado. Cosmos lo invoca por la ruta del ejecutable.
USER root
RUN mkdir -p /opt/dbt-venv /opt/extraccion && chown airflow:root /opt/dbt-venv /opt/extraccion
USER airflow
RUN python -m venv /opt/dbt-venv \
    && /opt/dbt-venv/bin/pip install --no-cache-dir "dbt-core==1.12.7" "dbt-postgres==1.11.0"

COPY --chown=airflow:root pyproject.toml README.md LICENSE /opt/extraccion/
COPY --chown=airflow:root src /opt/extraccion/src
RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    "astronomer-cosmos==1.16.0" \
    /opt/extraccion
