{#
  Usa el esquema configurado tal cual (staging, intermedia, marts...) en vez del
  comportamiento por defecto de dbt, que lo antepone con el esquema del perfil
  (analitica_staging). Así las capas tienen nombres estables en todos los entornos.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
