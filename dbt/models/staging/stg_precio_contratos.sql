-- Staging: lee la tabla xm_precio_contratos de la capa plata, sin cambiarla (EA3).
-- Se crea como VISTA: los modelos de marts leen de aqui.
select *
from {{ source('plata', 'xm_precio_contratos') }}