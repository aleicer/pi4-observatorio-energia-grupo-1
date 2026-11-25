-- MART del dashboard: la energia generada en el pais por tipo de planta, dia a dia.
-- Grano: una fecha y un tipo de planta (HIDRAULICA, TERMICA, SOLAR, EOLICA...). 2024-2026.
-- Responde la pregunta 3 (matriz de generacion) y la pregunta propia (cuanto compensa lo solar).
-- Pasa de 5,9 millones de filas (fecha, hora y planta) a unas 6.000: el dashboard carga rapido.

select
    g.fecha_id,
    d.fecha,
    d.periodo,
    d.anio,
    d.mes,
    d.fase_enso,
    -- Temporada seca en Colombia: diciembre a marzo y julio-agosto (llueve menos)
    d.mes in (12, 1, 2, 3, 7, 8)      as es_temporada_seca,
    r.tipo,
    sum(g.generacion_kwh) / 1e6       as generacion_gwh
from {{ ref('fact_generacion_recurso') }} as g
join {{ ref('dim_recurso') }} as r on g.recurso_id = r.recurso_id
join {{ ref('dim_fecha') }}    as d on g.fecha_id = d.fecha_id
group by all
order by g.fecha_id, r.tipo