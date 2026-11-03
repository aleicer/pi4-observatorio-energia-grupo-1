-- Staging: lee la tabla noaa_oni_mensual de la capa plata, sin cambiarla.
-- Se crea como VISTA: los modelos de marts leen de aqui.
select *
from {{ source('plata', 'noaa_oni_mensual') }}
