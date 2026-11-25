-- Prueba del GRANO de mart_ventas_costo_mensual: el mismo de fact_ventas_mensual
-- (un mes, un municipio, un segmento y un tipo de compra). Si la union con los precios
-- duplicara filas, esta prueba lo detecta.
select fecha_id, municipio_id, segmento, tipo_compra, count(*) as filas
from {{ ref('mart_ventas_costo_mensual') }}
group by all
having count(*) > 1