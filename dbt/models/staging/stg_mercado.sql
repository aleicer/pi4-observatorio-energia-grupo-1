-- Staging: lee la tabla xm_mercado_horario de la capa plata, sin cambiarla.
-- Se crea como VISTA: los modelos de marts leen de aqui.
select *
from {{ source('plata', 'xm_mercado_horario') }}
