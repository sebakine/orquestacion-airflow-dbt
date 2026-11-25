{#
  dbt usa `now()::timestamp` para cerrar versiones; las columnas del snapshot son
  timestamptz porque `actualizado_utc` lo es. Se devuelve timestamptz para que coincidan.
#}
{% macro postgres__snapshot_get_time() -%}
    now()
{%- endmacro %}
