{% docs __overview__ %}
# Datos públicos de Chile: sismos e indicadores económicos

Proyecto dbt del repositorio [orquestacion-airflow-dbt](https://github.com/sebakine/orquestacion-airflow-dbt).

Airflow carga los datos crudos en el esquema `raw` y dbt los transforma en capas:

| Capa | Esquema | Qué tiene |
|---|---|---|
| Staging | `staging` | Una vista por tabla de origen, con tipos y nombres en español. |
| Intermedia | `intermedia` | Reglas de negocio: filtrar sismos reales, ubicar regiones, completar días sin publicación. |
| Marts | `marts` | Tablas de hechos y dimensiones (modelo estrella) y agregados listos para dashboards. |
| Snapshots | `snapshots` | Historial de revisiones de cada sismo (SCD tipo 2). |

Usa el grafo de linaje (botón abajo a la derecha) para ver de dónde sale cada tabla.
{% enddocs %}
