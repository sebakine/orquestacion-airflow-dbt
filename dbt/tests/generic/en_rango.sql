{% test en_rango(model, column_name, minimo=none, maximo=none) %}
{# Falla con las filas cuyo valor queda fuera de [minimo, maximo]. Los null no cuentan. #}
select {{ column_name }}
from {{ model }}
where {{ column_name }} is not null
  and (
    false
    {% if minimo is not none %} or {{ column_name }} < {{ minimo }} {% endif %}
    {% if maximo is not none %} or {{ column_name }} > {{ maximo }} {% endif %}
  )
{% endtest %}
