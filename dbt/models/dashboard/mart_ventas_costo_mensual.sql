-- MART del dashboard: las ventas de EnerAndes con lo que costo comprar esa energia.
-- Grano: un mes, un municipio, un segmento y un tipo de compra (el mismo de fact_ventas_mensual).
-- Responde la pregunta 5: cuanto habria costado comprar en bolsa en vez de por contrato,
-- y que municipios y segmentos concentran el riesgo.
--
-- Supuesto (va en las limitaciones del informe): EnerAndes compra al precio promedio del
-- mercado: la energia "Contrato" al precio promedio de contratos de XM y la energia "Bolsa"
-- al precio de bolsa del mes, ponderado por la demanda.

with precios as (
    select
        fecha_id,
        precio_bolsa_cop_kwh,
        precio_contrato_cop_kwh,
        fase_enso
    from {{ ref('mart_hidroclima_mensual') }}
)

select
    v.fecha_id,
    d.periodo,
    d.anio,
    d.mes,
    p.fase_enso,
    v.municipio_id,
    mu.municipio,
    s.segmento,
    v.tipo_compra,
    v.energia_kwh,
    v.valor_cop,
    v.clientes,
    p.precio_bolsa_cop_kwh,
    p.precio_contrato_cop_kwh,
    -- Lo que costo comprar la energia, segun como se compro
    v.energia_kwh * case
        when v.tipo_compra = 'Bolsa' then p.precio_bolsa_cop_kwh
        else p.precio_contrato_cop_kwh
    end as costo_compra_cop,
    -- Los dos escenarios: toda esta energia comprada en bolsa o toda por contrato
    v.energia_kwh * p.precio_bolsa_cop_kwh
        as costo_si_bolsa_cop,
    v.energia_kwh * p.precio_contrato_cop_kwh
        as costo_si_contrato_cop
from {{ ref('fact_ventas_mensual') }} as v
join {{ ref('dim_fecha') }} as d on v.fecha_id = d.fecha_id
join {{ ref('dim_municipio') }} as mu on v.municipio_id = mu.municipio_id
join {{ ref('dim_segmento') }} as s on v.segmento_id = s.segmento_id
left join precios as p on v.fecha_id = p.fecha_id