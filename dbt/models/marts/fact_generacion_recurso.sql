-- HECHOS: la energia que genero cada planta, hora por hora (XM).
-- Grano: una fecha, una hora y una planta.

select
    cast(strftime(fecha, '%Y%m%d') as integer)  as fecha_id,
    hora,
    recurso_id,
    -- Medida
    generacion_kwh
from {{ ref('stg_generacion') }}
