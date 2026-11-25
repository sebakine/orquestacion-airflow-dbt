-- Sismos que USGS revisó después de publicarlos, con el cambio de magnitud.
-- Sale del snapshot, así que solo ve las revisiones ocurridas desde que el pipeline corre.
with versiones as (
    select
        sismo_id,
        magnitud,
        estado_revision,
        dbt_valid_from,
        row_number() over (partition by sismo_id order by dbt_valid_from) as version,
        count(*) over (partition by sismo_id) as total_versiones
    from {{ ref('snap_usgs_sismos') }}
)

select
    sismo_id,
    max(total_versiones) as versiones,
    max(magnitud) filter (where version = 1) as magnitud_inicial,
    max(magnitud) filter (where version = total_versiones) as magnitud_actual,
    max(magnitud) filter (where version = total_versiones)
        - max(magnitud) filter (where version = 1) as cambio_magnitud,
    max(estado_revision) filter (where version = 1) as estado_inicial,
    max(estado_revision) filter (where version = total_versiones) as estado_actual,
    min(dbt_valid_from) as primera_version_en,
    max(dbt_valid_from) as ultima_revision_en
from versiones
where total_versiones > 1
group by sismo_id
