{# Convierte un timestamptz a la fecha calendario en Chile. #}
{% macro fecha_chile(columna) -%}
    ({{ columna }} at time zone '{{ var("zona_horaria") }}')::date
{%- endmacro %}
