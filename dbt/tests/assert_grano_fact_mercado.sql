-- Prueba del GRANO de fact_mercado_horario: una sola fila por fecha y hora.
select fecha_id, hora, count(*) as filas
from {{ ref('fact_mercado_horario') }}
group by all
having count(*) > 1
