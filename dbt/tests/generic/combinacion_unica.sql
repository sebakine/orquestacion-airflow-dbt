{% test combinacion_unica(model, columnas) %}
{# Falla si alguna combinación de columnas se repite (clave compuesta). #}
select {{ columnas | join(', ') }}, count(*) as repeticiones
from {{ model }}
group by {{ columnas | join(', ') }}
having count(*) > 1
{% endtest %}
