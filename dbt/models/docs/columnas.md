{# Descripciones de columnas que se repiten en varios modelos. Se usan con doc('col_...'). #}

{% docs col_sismo_id %}Identificador del sismo en USGS, por ejemplo `us6000phap`.{% enddocs %}
{% docs col_origen_utc %}Momento en que ocurrió el sismo, en UTC.{% enddocs %}
{% docs col_origen_hora_chile %}Momento en que ocurrió el sismo, en hora de Chile (America/Santiago).{% enddocs %}
{% docs col_actualizado_utc %}Última vez que USGS modificó el evento, en UTC. Cambia con cada revisión.{% enddocs %}
{% docs col_actualizado_ms %}Última modificación del evento en USGS, en milisegundos desde 1970 (campo `updated` del GeoJSON).{% enddocs %}
{% docs col_cargado_en %}Cuándo llegó esta versión del registro al warehouse. La usa la carga incremental.{% enddocs %}
{% docs col_ejecucion %}Identificador de la corrida de Airflow que cargó el registro.{% enddocs %}
{% docs col_payload %}Respuesta original de la API en JSON, sin transformar.{% enddocs %}
{% docs col_magnitud %}Magnitud del sismo.{% enddocs %}
{% docs col_tipo_magnitud %}Escala de la magnitud: `mww` (momento), `mb` (ondas de cuerpo), `ml` (local), etc.{% enddocs %}
{% docs col_latitud %}Latitud del epicentro en grados (negativa al sur del ecuador).{% enddocs %}
{% docs col_longitud %}Longitud del epicentro en grados (negativa al oeste de Greenwich).{% enddocs %}
{% docs col_profundidad_km %}Profundidad del hipocentro en kilómetros.{% enddocs %}
{% docs col_lugar %}Descripción del lugar que publica USGS, por ejemplo `45 km W of Coquimbo, Chile`.{% enddocs %}
{% docs col_distancia_km %}Distancia en kilómetros a la ciudad de referencia, sacada del texto de `lugar`.{% enddocs %}
{% docs col_direccion %}Rumbo desde la ciudad de referencia hacia el epicentro (N, SW, ENE...).{% enddocs %}
{% docs col_ciudad_referencia %}Ciudad más cercana que menciona USGS en `lugar`.{% enddocs %}
{% docs col_pais %}País que menciona USGS al final de `lugar`.{% enddocs %}
{% docs col_estado_revision %}`automatic` cuando lo calculó un algoritmo y `reviewed` cuando lo revisó una persona.{% enddocs %}
{% docs col_tipo_evento %}Tipo de evento según USGS: `earthquake`, `quarry blast`, `explosion`, etc. Solo los `earthquake` pasan a los marts.{% enddocs %}
{% docs col_alerta_tsunami %}Verdadero si USGS marcó el evento con aviso de tsunami.{% enddocs %}
{% docs col_reportes_sentido %}Cantidad de personas que reportaron haberlo sentido en "Did You Feel It?" de USGS.{% enddocs %}
{% docs col_significancia %}Índice de USGS de 0 a 1000 que combina magnitud, reportes e impacto estimado.{% enddocs %}
{% docs col_url_usgs %}Página del evento en el sitio de USGS.{% enddocs %}
{% docs col_categoria %}Clasificación por magnitud: menor (< 4), ligero (< 5), moderado (< 6), fuerte (< 7) o mayor.{% enddocs %}
{% docs col_es_superficial %}Verdadero si la profundidad es menor de 70 km.{% enddocs %}
{% docs col_region_codigo %}Código oficial de la región de Chile. Nulo si el sismo ocurrió fuera de Chile.{% enddocs %}
{% docs col_region_nombre %}Nombre de la región de Chile.{% enddocs %}
{% docs col_orden_norte_sur %}Posición de la región de norte a sur, para ordenar gráficos.{% enddocs %}
{% docs col_lat_desde %}Latitud mínima del rectángulo que aproxima la región.{% enddocs %}
{% docs col_lat_hasta %}Latitud máxima del rectángulo que aproxima la región.{% enddocs %}
{% docs col_lon_desde %}Longitud mínima del rectángulo que aproxima la región.{% enddocs %}
{% docs col_lon_hasta %}Longitud máxima del rectángulo que aproxima la región.{% enddocs %}
{% docs col_prioridad %}Desempate cuando un punto cae en dos rectángulos: gana el número menor (la Región Metropolitana va primero).{% enddocs %}
{% docs col_fecha %}Fecha calendario en hora de Chile.{% enddocs %}
{% docs col_fecha_original %}Fecha tal como la entrega la API, antes de convertirla.{% enddocs %}
{% docs col_anio %}Año.{% enddocs %}
{% docs col_trimestre %}Trimestre del año (1 a 4).{% enddocs %}
{% docs col_dia %}Día del mes.{% enddocs %}
{% docs col_dia_semana %}Día de la semana ISO: 1 es lunes y 7 es domingo.{% enddocs %}
{% docs col_nombre_dia %}Nombre del día de la semana en español.{% enddocs %}
{% docs col_nombre_mes %}Nombre del mes en español.{% enddocs %}
{% docs col_inicio_mes %}Primer día del mes de la fecha.{% enddocs %}
{% docs col_es_fin_de_semana %}Verdadero si la fecha cae sábado o domingo.{% enddocs %}
{% docs col_indicador_codigo %}Código del indicador en mindicador.cl: `dolar`, `euro`, `uf`, `utm` o `libra_cobre`.{% enddocs %}
{% docs col_indicador_nombre %}Nombre del indicador según mindicador.cl.{% enddocs %}
{% docs col_unidad_medida %}Unidad en que se expresa el valor: `Pesos` o `Dólar`.{% enddocs %}
{% docs col_periodicidad %}Cada cuánto se publica el indicador: diaria o mensual.{% enddocs %}
{% docs col_dias_arrastre %}Máximo de días seguidos que se rellena con el último valor publicado antes de dejar el día vacío.{% enddocs %}
{% docs col_valor %}Valor del indicador en su unidad de medida.{% enddocs %}
{% docs col_es_valido %}Falso si la fecha o el valor no se pudieron interpretar.{% enddocs %}
{% docs col_es_publicado %}Falso cuando el valor se arrastró desde el último día publicado.{% enddocs %}
{% docs col_variacion_diaria_pct %}Variación porcentual respecto del día anterior.{% enddocs %}
{% docs col_dolar %}Dólar observado en pesos chilenos.{% enddocs %}
{% docs col_dolar_variacion_pct %}Variación porcentual del dólar respecto del día anterior.{% enddocs %}
{% docs col_euro %}Euro en pesos chilenos.{% enddocs %}
{% docs col_uf %}Unidad de Fomento en pesos chilenos.{% enddocs %}
{% docs col_utm %}Unidad Tributaria Mensual en pesos chilenos.{% enddocs %}
{% docs col_libra_cobre_usd %}Precio de la libra de cobre en dólares.{% enddocs %}
{% docs col_sismos %}Cantidad de sismos.{% enddocs %}
{% docs col_sismos_m5_o_mas %}Cantidad de sismos de magnitud 5 o más.{% enddocs %}
{% docs col_magnitud_maxima %}Magnitud del sismo más fuerte.{% enddocs %}
{% docs col_magnitud_promedio %}Magnitud promedio.{% enddocs %}
{% docs col_profundidad_promedio_km %}Profundidad promedio en kilómetros.{% enddocs %}
{% docs col_versiones %}Cantidad de versiones que guardó el snapshot para el sismo.{% enddocs %}
{% docs col_magnitud_inicial %}Magnitud de la primera versión publicada.{% enddocs %}
{% docs col_magnitud_actual %}Magnitud de la última versión publicada.{% enddocs %}
{% docs col_cambio_magnitud %}Magnitud actual menos magnitud inicial.{% enddocs %}
{% docs col_estado_inicial %}Estado de revisión de la primera versión.{% enddocs %}
{% docs col_estado_actual %}Estado de revisión de la última versión.{% enddocs %}
{% docs col_primera_version_en %}Cuándo se guardó la primera versión en el snapshot.{% enddocs %}
{% docs col_ultima_revision_en %}Cuándo se guardó la última versión en el snapshot.{% enddocs %}
{% docs col_descripcion %}Descripción del indicador.{% enddocs %}
{% docs col_dbt_scd_id %}Identificador único de la versión, generado por dbt.{% enddocs %}
{% docs col_dbt_updated_at %}Valor de `actualizado_utc` con que dbt registró la versión.{% enddocs %}
{% docs col_dbt_valid_from %}Desde cuándo es válida esta versión.{% enddocs %}
{% docs col_dbt_valid_to %}Hasta cuándo fue válida esta versión. Nulo en la versión vigente.{% enddocs %}
