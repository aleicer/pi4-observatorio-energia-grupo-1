-- Dimension RECURSO: una planta de generacion, a partir del catalogo ListadoRecursos de XM.
-- Grano: una planta. Llave: recurso_id (codigo SIC de XM, por ejemplo '2QBW').
-- Las plantas que generan pero no estaban en el catalogo llegan de plata con tipo 'DESCONOCIDO'.

select
    recurso_id,
    nombre,
    tipo,                       -- HIDRAULICA, TERMICA, SOLAR, EOLICA, COGENERADOR o DESCONOCIDO
    fuente_energia,             -- AGUA, GAS, CARBON, RAD SOLAR, VIENTO...
    despacho,                   -- DESPACHADO CENTRALMENTE o NO DESPACHADO CENTRALMENTE
    clase,
    agente,
    fecha_operacion,
    estado,
    tipo in ('HIDRAULICA', 'SOLAR', 'EOLICA')   as es_renovable
from {{ ref('stg_recursos') }}
