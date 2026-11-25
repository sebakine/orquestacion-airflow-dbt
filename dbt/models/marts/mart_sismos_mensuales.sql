-- Actividad sísmica por mes y región, lista para un dashboard.
select
    f.inicio_mes as mes,
    coalesce(r.region_nombre, 'Fuera de Chile') as region,
    coalesce(r.orden_norte_sur, 99) as orden_norte_sur,
    count(*) as sismos,
    count(*) filter (where s.magnitud >= 5) as sismos_m5_o_mas,
    max(s.magnitud) as magnitud_maxima,
    round(avg(s.magnitud), 2) as magnitud_promedio,
    round(avg(s.profundidad_km), 1) as profundidad_promedio_km
from {{ ref('fct_sismos') }} as s
inner join {{ ref('dim_fecha') }} as f using (fecha)
left join {{ ref('dim_region') }} as r using (region_codigo)
group by 1, 2, 3
