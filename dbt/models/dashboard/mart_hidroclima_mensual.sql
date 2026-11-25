-- MART del dashboard: la situacion hidrica, el clima y el precio de la energia, mes a mes.
-- Grano: un mes (2015-01 a 2026-09). Responde las preguntas 1 (riesgo hidrico),
-- 2 (clima -> precio) y la pregunta propia (radiacion solar en El Nino).
-- Une 5 fuentes: XM (embalses, aportes, bolsa, contratos), NOAA (ONI), IDEAM y NASA POWER.

with meses as (
    -- Un mes por fila, con su ONI y su fase ENSO (estan en dim_fecha, iguales todo el mes)
    select
        periodo,
        min(fecha_id)                   as fecha_id,
        min(anio)                       as anio,
        min(mes)                        as mes,
        min(nombre_mes)                 as nombre_mes,
        min(oni)                        as oni,
        min(fase_enso)                  as fase_enso
    from {{ ref('dim_fecha') }}
    group by periodo
),

hidrologia as (
    select
        d.periodo,
        avg(h.volumen_util_pct)         as volumen_util_pct,
        min(h.volumen_util_pct)         as volumen_util_min_pct,
        sum(h.aportes_kwh) / 1e6        as aportes_gwh
    from {{ ref('fact_hidrologia_diaria') }} as h
    join {{ ref('dim_fecha') }} as d on h.fecha_id = d.fecha_id
    group by d.periodo
),

mercado as (
    select
        d.periodo,
        sum(m.precio_bolsa_cop_kwh * m.demanda_kwh) / sum(m.demanda_kwh) as precio_bolsa_cop_kwh,
        max(m.precio_bolsa_cop_kwh)    as precio_bolsa_max_cop_kwh,
        sum(m.demanda_kwh) / 1e6       as demanda_gwh
    from {{ ref('fact_mercado_horario') }} as m
    join {{ ref('dim_fecha') }} as d on m.fecha_id = d.fecha_id
    group by d.periodo
),

contratos as (
    select
        d.periodo,
        avg(c.precio_contrato_cop_kwh) as precio_contrato_cop_kwh
    from {{ ref('fact_precio_contrato_diario') }} as c
    join {{ ref('dim_fecha') }} as d on c.fecha_id = d.fecha_id
    group by d.periodo
),

lluvia_ideam as (
    select
        d.periodo,
        avg(c.precipitacion_mm)        as lluvia_ideam_mm_dia
    from {{ ref('fact_clima_diario') }} as c
    join {{ ref('dim_fecha') }} as d on c.fecha_id = d.fecha_id
    group by d.periodo
),

satelite as (
    select
        d.periodo,
        avg(case when s.punto not like 'La Guajira%' then s.precipitacion_mm end)
            as lluvia_nasa_mm_dia,
        avg(case when s.punto like 'La Guajira%' then s.radiacion_kwh_m2 end)
            as radiacion_guajira_kwh_m2
    from {{ ref('fact_clima_satelital') }} as s
    join {{ ref('dim_fecha') }} as d on s.fecha_id = d.fecha_id
    group by d.periodo
)

select
    m.fecha_id,
    m.periodo,
    m.anio,
    m.mes,
    m.nombre_mes,
    m.oni,
    m.fase_enso,
    h.volumen_util_pct,
    h.volumen_util_min_pct,
    h.aportes_gwh,
    k.precio_bolsa_cop_kwh,
    k.precio_bolsa_max_cop_kwh,
    k.demanda_gwh,
    c.precio_contrato_cop_kwh,
    i.lluvia_ideam_mm_dia,
    s.lluvia_nasa_mm_dia,
    s.radiacion_guajira_kwh_m2
from meses as m
left join hidrologia  as h on h.periodo = m.periodo
left join mercado     as k on k.periodo = m.periodo
left join contratos   as c on c.periodo = m.periodo
left join lluvia_ideam as i on i.periodo = m.periodo
left join satelite    as s on s.periodo = m.periodo
order by m.periodo