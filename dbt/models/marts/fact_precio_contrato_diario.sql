-- HECHOS: el precio promedio de los contratos de energia de Colombia cada dia (XM, EA3).
-- Grano: una fecha. Sirve para comparar lo que cuesta comprar por contrato frente a la bolsa.

select
    cast(strftime(fecha, '%Y%m%d') as integer) as fecha_id,
    -- Medida
    precio_contrato_cop_kwh
from {{ ref('stg_precio_contratos') }}