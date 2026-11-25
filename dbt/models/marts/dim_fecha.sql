-- Calendario desde var('fecha_inicio') hasta un año después de hoy.
with dias as (
    select generate_series(
        '{{ var("fecha_inicio") }}'::date,
        (current_date + interval '1 year')::date,
        interval '1 day'
    )::date as fecha
)

select
    fecha,
    extract(year from fecha)::int as anio,
    extract(quarter from fecha)::int as trimestre,
    extract(month from fecha)::int as mes,
    extract(day from fecha)::int as dia,
    extract(isodow from fecha)::int as dia_semana,
    (array['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
           'septiembre', 'octubre', 'noviembre', 'diciembre'])[extract(month from fecha)::int]
        as nombre_mes,
    (array['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'])
        [extract(isodow from fecha)::int] as nombre_dia,
    extract(isodow from fecha) in (6, 7) as es_fin_de_semana,
    date_trunc('month', fecha)::date as inicio_mes
from dias
