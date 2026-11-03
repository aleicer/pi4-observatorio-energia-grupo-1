-- Dimension SEGMENTO: una fila por segmento de cliente.
-- Grano: un segmento. Llave: segmento_id.

select
    -- row_number() numera los segmentos 1, 2, 3, 4 en orden alfabetico
    row_number() over (order by segmento)   as segmento_id,
    segmento
from (select distinct segmento from {{ ref('stg_ventas') }})
