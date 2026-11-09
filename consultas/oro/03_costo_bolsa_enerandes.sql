-- ¿Cuánto le habría costado a EnerAndes comprar en bolsa la energía de cada año?
with precio_mes as (
    select
        d.anio,
        d.mes,
        avg(m.precio_bolsa_cop_kwh) as precio
    from fact_mercado_horario as m
    join dim_fecha as d
        on m.fecha_id = d.fecha_id
    group by d.anio, d.mes
)
select
    d.anio,
    round(sum(v.energia_kwh) / 1e6, 1) as energia_gwh,
    round(
        sum(v.energia_kwh * p.precio) / 1e9,
        1
    ) as costo_en_bolsa_mil_millones_cop
from fact_ventas_mensual as v
join dim_fecha as d
    on v.fecha_id = d.fecha_id
join precio_mes as p
    on p.anio = d.anio
    and p.mes = d.mes
group by d.anio
order by d.anio;