-- HECHOS: la situacion hidrica del pais cada dia (XM).
-- Grano: una fecha.

select
    cast(strftime(fecha, '%Y%m%d') as integer)  as fecha_id,
    -- Medidas
    volumen_util_pct,               -- % de llenado de los embalses del pais
    aportes_kwh                     -- energia que traen los rios a los embalses
from {{ ref('stg_hidrologia') }}
