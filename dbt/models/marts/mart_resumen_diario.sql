-- Una fila por día con los indicadores en columnas y la actividad sísmica del día.
with indicadores as (
    select
        fecha,
        max(valor) filter (where indicador_codigo = 'dolar') as dolar,
        max(valor) filter (where indicador_codigo = 'euro') as euro,
        max(valor) filter (where indicador_codigo = 'uf') as uf,
        max(valor) filter (where indicador_codigo = 'utm') as utm,
        max(valor) filter (where indicador_codigo = 'libra_cobre') as libra_cobre_usd,
        max(variacion_diaria_pct) filter (where indicador_codigo = 'dolar')
            as dolar_variacion_pct
    from {{ ref('fct_indicadores_diarios') }}
    group by fecha
),

sismos as (
    select fecha, count(*) as sismos, max(magnitud) as magnitud_maxima
    from {{ ref('fct_sismos') }}
    group by fecha
)

select
    f.fecha,
    f.nombre_dia,
    f.es_fin_de_semana,
    i.dolar,
    i.dolar_variacion_pct,
    i.euro,
    i.uf,
    i.utm,
    i.libra_cobre_usd,
    coalesce(s.sismos, 0) as sismos,
    s.magnitud_maxima
from {{ ref('dim_fecha') }} as f
left join indicadores as i using (fecha)
left join sismos as s using (fecha)
where i.fecha is not null or s.fecha is not null
