-- La API publica cada valor con la medianoche de Chile expresada en UTC
-- ("2025-01-02T03:00:00.000Z"), así que la fecha correcta sale de convertir a America/Santiago.
-- Los valores que no son número o las fechas mal formadas quedan en null y con `es_valido = false`,
-- para revisarlos en vez de perderlos.
with fuente as (
    select * from {{ source('mindicador', 'mindicador_valores') }}
),

tipado as (
    select
        codigo as indicador_codigo,
        fecha as fecha_original,
        case
            when fecha ~ '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$'
                then {{ fecha_chile("fecha::timestamptz") }}
        end as fecha,
        case when jsonb_typeof(valor) = 'number' then valor::text::numeric end as valor,
        cargado_en
    from fuente
)

select
    *,
    fecha is not null and valor is not null and valor > 0 as es_valido
from tipado
