-- Dimension FECHA: un dia del calendario, del 1-ene-2023 al 30-sep-2026.
-- Grano: un dia. Llave: fecha_id (AAAAMMDD, por ejemplo 20260315).
-- Trae la fase del fenomeno ENSO (El Nino / La Nina / Neutral) del mes, desde NOAA.

with dias as (
    -- generate_series crea una lista con todos los dias del rango (vars de dbt_project.yml);
    -- unnest la convierte en una fila por dia
    select unnest(generate_series(
        cast('{{ var("fecha_inicio") }}' as date),
        cast('{{ var("fecha_fin") }}' as date),
        interval 1 day))::date as fecha
)

select
    -- La llave: la fecha como numero AAAAMMDD
    cast(strftime(d.fecha, '%Y%m%d') as integer)                    as fecha_id,
    d.fecha,
    year(d.fecha)                                                   as anio,
    month(d.fecha)                                                  as mes,
    -- Las listas de DuckDB empiezan en 1: [mes] toma el nombre del mes
    ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto',
     'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][month(d.fecha)]   as nombre_mes,
    strftime(d.fecha, '%Y-%m')                                      as periodo,
    quarter(d.fecha)                                                as trimestre,
    -- isodow: 1 = lunes ... 7 = domingo
    isodow(d.fecha)                                                 as dia_semana,
    ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado',
     'Domingo'][isodow(d.fecha)]                                    as nombre_dia,
    isodow(d.fecha) >= 6                                            as es_fin_de_semana,
    -- El ONI del mes (NOAA lo asigna al mes central del trimestre movil)
    o.oni,
    -- NOAA publica con un mes de atraso: los meses sin ONI quedan como 'Sin dato'
    coalesce(o.fase_enso, 'Sin dato')                               as fase_enso
from dias as d
left join {{ ref('stg_oni') }} as o
    on o.periodo = strftime(d.fecha, '%Y-%m')
