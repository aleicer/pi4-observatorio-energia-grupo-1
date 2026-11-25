-- Prueba del GRANO de mart_generacion_tipo_diaria: una sola fila por fecha y tipo de planta.
select fecha_id, tipo, count(*) as filas
from {{ ref('mart_generacion_tipo_diaria') }}
group by all
having count(*) > 1