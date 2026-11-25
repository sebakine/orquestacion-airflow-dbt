{{
    config(
        materialized='incremental',
        unique_key='sismo_id',
        incremental_strategy='merge',
        on_schema_change='fail',
    )
}}

-- Incremental: en cada corrida solo procesa los sismos que llegaron a raw (nuevos o
-- revisados por USGS) desde la corrida anterior, y los reemplaza por sismo_id.
-- El filtro usa `cargado_en` (hora de llegada al warehouse) y no `actualizado_utc`:
-- una revisión puede tener fecha de USGS anterior a la de otro sismo ya cargado, y se perdería.
select
    sismo_id,
    {{ fecha_chile('origen_utc') }} as fecha,
    region_codigo,
    origen_utc,
    (origen_utc at time zone '{{ var("zona_horaria") }}') as origen_hora_chile,
    magnitud,
    tipo_magnitud,
    case
        when magnitud < 4 then 'menor'
        when magnitud < 5 then 'ligero'
        when magnitud < 6 then 'moderado'
        when magnitud < 7 then 'fuerte'
        else 'mayor'
    end as categoria,
    profundidad_km,
    profundidad_km < 70 as es_superficial,
    latitud,
    longitud,
    lugar,
    ciudad_referencia,
    pais,
    distancia_km,
    estado_revision,
    alerta_tsunami,
    reportes_sentido,
    url_usgs,
    actualizado_utc,
    cargado_en
from {{ ref('int_sismos__ubicados') }}
{% if is_incremental() %}
where cargado_en > (select coalesce(max(cargado_en), '-infinity') from {{ this }})
{% endif %}
