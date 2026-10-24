# Bitácora – Jaider Morales

## Semana 2 (19 – 25 de octubre de 2026)

**Rol esta semana:** Data Quality Analyst

### 1. ¿Qué hice?

Durante esta semana me encargué de realizar pruebas automáticas para comprobar el funcionamiento de algunas partes del proyecto del Observatorio de Energía.

Primero tuve que preparar mi computador Mac para trabajar con el proyecto. Instalé Python 3.13, configuré el entorno virtual y las librerías necesarias. También trabajé con Git y GitHub para poder compartir mis avances con mis compañeros.

Después creé tres archivos de pruebas utilizando pytest:

**Pruebas de ventanas()**

En el archivo `tests/test_ventanas.py` hice tres pruebas para comprobar que la función dividiera correctamente los rangos de fechas en grupos de máximo 30 días.

También verifiqué que no se repitieran ni faltaran días y que funcionara correctamente con un rango de un solo día.

**Pruebas de aplanar()**

En el archivo `tests/test_aplanar.py` hice cuatro pruebas para revisar cómo se organizan los datos que llegan de XM.

Comprobé que la función pudiera trabajar con datos horarios, diarios y listas de recursos. También hice una prueba para verificar qué sucede cuando la respuesta está vacía.

Para realizar estas pruebas tuve que actualizar mi rama con los cambios que Aleicer había realizado en el código de XM.

**Pruebas de ya_existe()**

En el archivo `tests/test_idempotencia.py` realicé tres pruebas para comprobar que el programa pudiera reconocer cuándo un archivo ya había sido descargado.

También revisé que se pudiera volver a descargar cuando se utiliza la opción `forzar` y que el programa identificara cuando un archivo todavía no existe.

Al finalizar, ejecuté las pruebas utilizando el comando `python -m pytest -v` para comprobar su funcionamiento.

**Hallazgos de calidad**

También revisé el archivo `docs/perfilamiento.md`, donde encontré algunas situaciones que pueden afectar la calidad de los datos.

Entre ellas están los registros duplicados en los archivos de EnerAndes, fechas que no se reconocen correctamente, datos del IDEAM que no llegan hasta el final del periodo solicitado y valores nulos en algunas horas de generación de XM.

Con esta información preparé los hallazgos de calidad y las posibles acciones para revisarlos en la siguiente etapa del proyecto.

### 2. ¿Qué aprendí?

Durante esta actividad aprendí a utilizar pytest para comprobar el funcionamiento de funciones de Python.

Antes no tenía mucha experiencia haciendo pruebas automáticas, así que este trabajo me permitió entender cómo se pueden utilizar ejemplos de datos para verificar si una función entrega el resultado esperado.

También aprendí más sobre el manejo de Git y GitHub, especialmente sobre la creación de ramas, los commits, los Pull Requests y la integración de cambios realizados por otros compañeros.

Otra cosa que aprendí fue que antes de analizar los datos es importante revisar si tienen registros repetidos, valores vacíos o fechas incorrectas, porque estos problemas pueden afectar los resultados.

### 3. Dificultades y cómo las resolví

Una de las primeras dificultades fue la configuración de Python en mi Mac, porque tenía instalada la versión 3.9.6 y necesitaba una versión más reciente. Para solucionarlo instalé Python 3.13 y creé un entorno virtual para el proyecto.

Después tuve un problema con pytest, porque no estaba instalado. Cuando logré instalarlo, las pruebas no aparecían porque había creado el archivo `test_ventanas.py`, pero todavía estaba vacío. Luego agregué el código y pude ejecutar las primeras tres pruebas.

También tuve dificultades al intentar subir los cambios a GitHub, porque estaba utilizando una cuenta que no tenía permisos para modificar el repositorio. Después pude solucionar el acceso.

Otra dificultad fue entender cómo actualizar mi rama con los cambios que Aleicer estaba haciendo en XM. Al principio la función `aplanar()` no tenía soporte para las listas de recursos. Cuando Aleicer integró sus modificaciones, actualicé mi rama y pude realizar las cuatro pruebas.

Estas situaciones me ayudaron a conocer mejor el funcionamiento de las herramientas que estamos utilizando.

### 4. Horas dedicadas

**Total de horas:** 11 horas

### 5. Enlaces de mi trabajo

**Repositorio del proyecto:**

https://github.com/aleicer/pi4-observatorio-energia-grupo-1

**Commits realizados:**

**Commit 1 – Pruebas de ventanas():**

https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/c64ce53

**Commit 2 – Pruebas de aplanar():**

https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/798664f

**Commit 3 – Pruebas de idempotencia:**

https://github.com/aleicer/pi4-observatorio-energia-grupo-1/commit/120d7ac

**Pull Request de pruebas automáticas:**

https://github.com/aleicer/pi4-observatorio-energia-grupo-1/pull/2

**Pull Request de hallazgos y bitácora:**

[Agregar enlace cuando esté creado].