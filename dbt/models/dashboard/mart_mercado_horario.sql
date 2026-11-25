-- MART del dashboard: precio de bolsa y demanda hora por hora, con el calendario ya unido.
-- Grano: una fecha y una hora (2015-2026). Responde la pregunta 4 (patrones de demanda:
-- hora, dia de la semana y mes; hora pico) y sirve para ver el precio por franja.
-- Es una tabla "ancha": trae las columnas de dim_fecha y dim_hora para no unirlas en el dashboard.

select
    m.fecha_id,
    d.fecha,
    d.periodo,
    d.anio,
    d.mes,
    d.nombre_mes,
    d.dia_semana,
    d.nombre_dia,
    d.es_fin_de_semana,
    d.fase_enso,
    m.hora,
    h.franja,
    m.precio_bolsa_cop_kwh,
    m.demanda_kwh / 1e3 as demanda_mwh
from {{ ref('fact_mercado_horario') }} as m
join {{ ref('dim_fecha') }} as d on m.fecha_id = d.fecha_id
join {{ ref('dim_hora') }} as h on m.hora = h.hora
order by m.fecha_id, m.hora