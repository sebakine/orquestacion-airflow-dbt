-- Un valor por indicador y por cada día desde su primer dato hasta hoy.
-- Los días sin publicación (fines de semana y feriados para el dólar; todo el mes para la UTM)
-- toman el último valor publicado, y `es_publicado` indica cuál es cuál. El arrastre tiene un
-- tope por indicador (seed indicadores_catalogo) para no inventar valores si la carga se detiene.
with valores as (
    select indicador_codigo, fecha, valor
    from {{ ref('stg_mindicador__valores') }}
    where es_valido
),

rango as (
    select
        v.indicador_codigo,
        min(v.fecha) as desde,
        least(current_date, max(v.fecha) + c.dias_arrastre) as hasta
    from valores as v
    inner join {{ ref('indicadores_catalogo') }} as c using (indicador_codigo)
    group by v.indicador_codigo, c.dias_arrastre
),

calendario as (
    select r.indicador_codigo, f.fecha
    from rango as r
    inner join {{ ref('dim_fecha') }} as f
        on f.fecha between r.desde and r.hasta
),

unido as (
    select
        c.indicador_codigo,
        c.fecha,
        v.valor,
        -- Cada valor publicado abre un grupo; los días siguientes sin dato quedan en ese grupo.
        count(v.valor) over (
            partition by c.indicador_codigo order by c.fecha
        ) as grupo
    from calendario as c
    left join valores as v
        on v.indicador_codigo = c.indicador_codigo and v.fecha = c.fecha
)

select
    indicador_codigo,
    fecha,
    first_value(valor) over (
        partition by indicador_codigo, grupo order by fecha
    ) as valor,
    valor is not null as es_publicado
from unido
