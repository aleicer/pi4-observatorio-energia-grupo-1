-- ¿Cómo cambia el precio de bolsa según la fase de El Niño?
select
    d.anio,
    d.fase_enso,
    count(distinct d.fecha) as dias,
    round(avg(m.precio_bolsa_cop_kwh), 1) as precio_promedio_cop_kwh,
    round(max(m.precio_bolsa_cop_kwh), 1) as precio_maximo_cop_kwh
from fact_mercado_horario as m
join dim_fecha as d
    on m.fecha_id = d.fecha_id
group by d.anio, d.fase_enso
order by d.anio, d.fase_enso;