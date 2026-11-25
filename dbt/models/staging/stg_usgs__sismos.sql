-- Un sismo por fila, con tipos y nombres en español. Sin filtros: eso ocurre en la capa intermedia.
with fuente as (
    select * from {{ source('usgs', 'usgs_eventos') }}
)

select
    id as sismo_id,
    to_timestamp((payload -> 'properties' ->> 'time')::bigint / 1000.0) as origen_utc,
    to_timestamp(actualizado_ms / 1000.0) as actualizado_utc,
    (payload -> 'properties' ->> 'mag')::numeric(4, 2) as magnitud,
    payload -> 'properties' ->> 'magType' as tipo_magnitud,
    (payload -> 'geometry' -> 'coordinates' ->> 1)::numeric(8, 4) as latitud,
    (payload -> 'geometry' -> 'coordinates' ->> 0)::numeric(8, 4) as longitud,
    (payload -> 'geometry' -> 'coordinates' ->> 2)::numeric(7, 2) as profundidad_km,
    payload -> 'properties' ->> 'place' as lugar,
    payload -> 'properties' ->> 'type' as tipo_evento,
    payload -> 'properties' ->> 'status' as estado_revision,
    (payload -> 'properties' ->> 'tsunami')::int = 1 as alerta_tsunami,
    (payload -> 'properties' ->> 'felt')::int as reportes_sentido,
    (payload -> 'properties' ->> 'sig')::int as significancia,
    payload -> 'properties' ->> 'url' as url_usgs,
    cargado_en
from fuente
