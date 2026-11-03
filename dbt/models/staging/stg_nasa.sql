-- Staging: lee la tabla nasa_power_diario de la capa plata, sin cambiarla.
-- Se crea como VISTA: los modelos de marts leen de aqui.
select *
from {{ source('plata', 'nasa_power_diario') }}
