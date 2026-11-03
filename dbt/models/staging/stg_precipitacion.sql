-- Staging: lee la tabla ideam_precipitacion_diaria de la capa plata, sin cambiarla.
-- Se crea como VISTA: los modelos de marts leen de aqui.
select *
from {{ source('plata', 'ideam_precipitacion_diaria') }}
