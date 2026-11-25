-- La UF se reajusta por inflación: de un día al otro casi nunca cambia más de 0,5 %.
-- Un salto mayor suele ser un error de carga (por ejemplo, un valor con separador equivocado).
select fecha, valor, variacion_diaria_pct
from {{ ref('fct_indicadores_diarios') }}
where indicador_codigo = 'uf'
  and abs(variacion_diaria_pct) > 0.5
