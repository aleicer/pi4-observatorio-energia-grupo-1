-- Prueba del GRANO de fact_clima_diario: una sola fila por fecha y estación.
select fecha_id, estacion_id, count(*) as filas
from {{ ref('fact_clima_diario') }}
group by all
having count(*) > 1
