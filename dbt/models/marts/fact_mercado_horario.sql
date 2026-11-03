-- HECHOS: el mercado de energia de Colombia hora por hora (XM).
-- Grano: una fecha y una hora.

select
    cast(strftime(fecha, '%Y%m%d') as integer)  as fecha_id,
    hora,
    -- Medidas
    precio_bolsa_cop_kwh,
    demanda_kwh
from {{ ref('stg_mercado') }}
