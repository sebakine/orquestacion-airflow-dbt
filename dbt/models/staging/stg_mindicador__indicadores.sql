select
    codigo as indicador_codigo,
    nombre as indicador_nombre,
    unidad_medida,
    cargado_en
from {{ source('mindicador', 'mindicador_indicadores') }}
