select
    indicador_codigo,
    fecha,
    valor,
    es_publicado,
    round(
        100.0 * (valor / nullif(lag(valor) over w, 0) - 1), 4
    ) as variacion_diaria_pct
from {{ ref('int_indicadores__diario_completo') }}
window w as (partition by indicador_codigo order by fecha)
