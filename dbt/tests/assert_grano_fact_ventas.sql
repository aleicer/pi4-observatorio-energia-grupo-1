-- Prueba del GRANO de fact_ventas_mensual: no puede haber dos filas con el mismo
-- mes, municipio, segmento y tipo de compra. La prueba pasa si devuelve 0 filas.
select fecha_id, municipio_id, segmento_id, tipo_compra, count(*) as filas
from {{ ref('fact_ventas_mensual') }}
group by all
having count(*) > 1
