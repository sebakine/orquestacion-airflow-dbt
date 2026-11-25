.PHONY: up down logs test test-dags dbt-build docs backfill lint

DBT = /opt/dbt-venv/bin/dbt
EXEC = docker compose exec airflow-scheduler

up:  ## Levanta Airflow, dbt y PostgreSQL (http://localhost:8080)
	docker compose up -d --build

down:  ## Detiene todo (los datos quedan en el volumen pgdata)
	docker compose down

logs:
	docker compose logs -f airflow-scheduler

lint:
	uv run ruff format --check src tests dags
	uv run ruff check src tests dags
	uv run mypy

test:  ## Extracción y dbt de punta a punta (necesita TEST_DATABASE_URL y dbt)
	uv run pytest --cov -m "not airflow"

test-dags:  ## Valida los DAGs dentro de la imagen de Airflow
	docker compose run --rm --no-deps -e AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags \
		-v $(PWD)/tests:/opt/airflow/tests airflow-scheduler bash -c \
		"airflow db migrate > /dev/null && pip install -q pytest && python -m pytest -p no:cacheprovider tests/test_dags.py"

dbt-build:  ## dbt build manual dentro del contenedor
	$(EXEC) bash -c "cd /opt/airflow/dbt && DBT_HOST=postgres DBT_PASSWORD=warehouse $(DBT) build --profiles-dir . --target-path /tmp/dbt-target --log-path /tmp/dbt-logs"

backfill:  ## Ejemplo: make backfill DESDE=2025-01-01 HASTA=2025-01-31
	$(EXEC) airflow backfill create --dag-id extraccion_sismos --from-date $(DESDE) --to-date $(HASTA)
