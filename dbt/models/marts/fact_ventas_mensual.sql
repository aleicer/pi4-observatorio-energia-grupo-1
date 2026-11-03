-- HECHOS: las ventas de energia de EnerAndes, 2023 a 2026.
-- Grano: un mes, un municipio, un segmento y un tipo de compra.
-- El mes se une con dim_fecha en su primer dia (2024-03 -> 20240301).

select
    cast(replace(v.periodo, '-', '') || '01' as integer)   as fecha_id,
    v.divipola                                              as municipio_id,
    s.segmento_id,
    v.tipo_compra,                                          -- Bolsa o Contrato
    -- Medidas
    v.energia_kwh,
    v.valor_cop,
    v.clientes
from {{ ref('stg_ventas') }} as v
join {{ ref('dim_segmento') }} as s
    on v.segmento = s.segmento
