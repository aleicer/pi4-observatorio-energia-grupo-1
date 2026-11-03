-- Dimension HORA: una hora del dia (0 = de 00:00 a 01:00 ... 23 = de 23:00 a 24:00).
-- Grano: una hora. Llave: hora.
-- franja: Pico (17 a 21 h, cuando la demanda y el precio son mas altos),
-- Valle (0 a 5 h, madrugada) y Media (el resto).

select
    h                                       as hora,
    lpad(cast(h as varchar), 2, '0') || ':00'   as hora_inicio,
    case
        when h between 17 and 21 then 'Pico'
        when h between 0 and 5   then 'Valle'
        else 'Media'
    end                                     as franja
from (select unnest(range(24)) as h)
