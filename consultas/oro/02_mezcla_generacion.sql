-- ¿Qué proporción de la energía viene de cada tipo de planta, por año?
select
    d.anio,
    r.tipo,
    round(sum(g.generacion_kwh) / 1e9, 2) as generacion_twh,
    round(
        100 * sum(g.generacion_kwh)
        / sum(sum(g.generacion_kwh)) over (partition by d.anio),
        1
    ) as porcentaje
from fact_generacion_recurso as g
join dim_fecha as d
    on g.fecha_id = d.fecha_id
join dim_recurso as r
    on g.recurso_id = r.recurso_id
group by d.anio, r.tipo
order by d.anio, generacion_twh desc;