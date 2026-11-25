{% test no_futuro(model, column_name, tolerancia="1 hour") %}
{# Una fecha en el futuro indica un error de zona horaria o un dato corrupto. #}
select {{ column_name }}
from {{ model }}
where {{ column_name }} > now() + interval '{{ tolerancia }}'
{% endtest %}
