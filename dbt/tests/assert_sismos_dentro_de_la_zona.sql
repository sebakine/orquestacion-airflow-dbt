-- Todo sismo debe estar dentro del rectángulo que se pide a USGS (Chile y su costa).
select sismo_id, latitud, longitud
from {{ ref('fct_sismos') }}
where latitud not between -56 and -17.5
   or longitud not between -76 and -66
