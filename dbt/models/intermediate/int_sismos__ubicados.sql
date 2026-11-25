-- Solo sismos (no explosiones de faenas mineras) con magnitud, ubicados en una región.
-- El lugar de USGS viene como "84 km NNW of Calama, Chile" o solo "Calama, Chile".
with sismos as (
    select * from {{ ref('stg_usgs__sismos') }}
    where tipo_evento = 'earthquake'
      and magnitud is not null
      and estado_revision <> 'deleted'
),

lugar as (
    select
        *,
        regexp_match(lugar, '^(\d+(?:\.\d+)?) km ([NSEW]{1,3}) of (.+)$') as partes
    from sismos
),

separado as (
    select
        *,
        partes[1]::numeric(6, 1) as distancia_km,
        partes[2] as direccion,
        coalesce(partes[3], lugar) as referencia
    from lugar
),

con_pais as (
    select
        *,
        nullif(trim(split_part(referencia, ',', 1)), '') as ciudad_referencia,
        case
            when referencia like '%,%' then trim(regexp_replace(referencia, '^.*,', ''))
            else 'Desconocido'
        end as pais
    from separado
),

region as (
    -- Primera región (por prioridad) cuyo rectángulo contiene el epicentro.
    select distinct on (s.sismo_id)
        s.sismo_id,
        r.region_codigo
    from con_pais as s
    inner join {{ ref('regiones_chile') }} as r
        on s.latitud between r.lat_desde and r.lat_hasta
        and s.longitud between r.lon_desde and r.lon_hasta
    order by s.sismo_id, r.prioridad
)

select
    s.sismo_id,
    s.origen_utc,
    s.actualizado_utc,
    s.magnitud,
    s.tipo_magnitud,
    s.latitud,
    s.longitud,
    s.profundidad_km,
    s.lugar,
    s.distancia_km,
    s.direccion,
    s.ciudad_referencia,
    s.pais,
    -- La región solo se asigna si USGS dice que la referencia está en Chile.
    case when s.pais = 'Chile' then r.region_codigo end as region_codigo,
    s.estado_revision,
    s.alerta_tsunami,
    s.reportes_sentido,
    s.url_usgs,
    s.cargado_en
from con_pais as s
left join region as r on r.sismo_id = s.sismo_id
