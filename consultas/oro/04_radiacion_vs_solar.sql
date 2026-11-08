-- Pregunta propia: ¿sube la radiación solar y la generación solar en los meses de El Niño?
select
    d.fase_enso,
    round(avg(c.radiacion_kwh_m2), 2) as radiacion_promedio_kwh_m2,
    round(
        sum(g.generacion_kwh) / 1e6 / count(distinct d.periodo),
        1
    ) as solar_gwh_por_mes
from dim_fecha as d
join fact_clima_satelital as c
    on c.fecha_id = d.fecha_id
    and c.punto like 'La Guajira%'
left join (
    select
        g.fecha_id,
        sum(g.generacion_kwh) as generacion_kwh
    from fact_generacion_recurso as g
    join dim_recurso as r
        on g.recurso_id = r.recurso_id
    where r.tipo = 'SOLAR'
    group by g.fecha_id
) as g
    on g.fecha_id = d.fecha_id
group by d.fase_enso
order by radiacion_promedio_kwh_m2 desc;