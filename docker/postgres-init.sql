-- Un solo PostgreSQL con dos bases: la de metadatos de Airflow y el data warehouse.
CREATE USER airflow WITH PASSWORD 'airflow';
CREATE DATABASE airflow OWNER airflow;
CREATE USER warehouse WITH PASSWORD 'warehouse';
CREATE DATABASE warehouse OWNER warehouse;
