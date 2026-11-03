-- Dimension MUNICIPIO: un municipio de Antioquia con su codigo DIVIPOLA (DANE).
-- Grano: un municipio. Llave: municipio_id (5 digitos, por ejemplo '05001' = Medellin).
-- Incluye los municipios con ventas de EnerAndes y cuantas estaciones del IDEAM tienen.

with municipios as (
    select distinct divipola as municipio_id, municipio
    from {{ ref('stg_ventas') }}
)

select
    m.municipio_id,
    m.municipio,
    count(e.estacion_id)        as estaciones_ideam
from municipios as m
left join {{ ref('stg_estaciones') }} as e
    on e.divipola = m.municipio_id
group by m.municipio_id, m.municipio
