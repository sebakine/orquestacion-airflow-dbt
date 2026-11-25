select
    i.indicador_codigo,
    i.indicador_nombre,
    i.unidad_medida,
    c.periodicidad,
    c.descripcion
from {{ ref('stg_mindicador__indicadores') }} as i
left join {{ ref('indicadores_catalogo') }} as c using (indicador_codigo)
