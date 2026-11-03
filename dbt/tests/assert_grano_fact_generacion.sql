-- Prueba del GRANO de fact_generacion_recurso: una sola fila por fecha, hora y planta.
select fecha_id, hora, recurso_id, count(*) as filas
from {{ ref('fact_generacion_recurso') }}
group by all
having count(*) > 1
