select
    region_codigo,
    region_nombre,
    orden_norte_sur
from {{ ref('regiones_chile') }}
