# Práctica 4 · Recomendación y grafo · EnVivo (fase 4)

Punto de partida de la práctica 4 de **Ampliación de Bases de Datos** (u-tad).
Aquí están el esqueleto de la carga del grafo, el de las siete consultas, los
datos con los que se construye el grafo y las pruebas con las que puedes
comprobarlo todo mientras lo escribes.

**El modelo del grafo lo diseñáis vosotros.** Empieza por leer las siete
consultas del enunciado y los ficheros de `datos/`, y decide el modelo antes de
escribir la carga. No se entrega aparte: se deduce del grafo que construye tu
`carga.py`.

El enunciado completo, con lo que pide cada consulta y la rúbrica, está en el
campus virtual. Esto es solo el código.

## Cómo empezar

1. **Crea tu repositorio a partir de esta plantilla** con el botón
   *Use this template → Create a new repository*, y márcalo como **Private**.
   No hagas un *fork*: un fork de un repositorio público es público, y tu
   código quedaría a la vista de todos. Uno por grupo: quien lo crea añade a
   su compañero en *Settings → Collaborators*.
2. Clónalo en tu máquina:

   ```bash
   git clone https://github.com/<tu-usuario>/abd-p4-grafo.git
   cd abd-p4-grafo
   ```

3. Levanta Neo4j, desde la carpeta donde tengas el `compose.yaml` de la
   asignatura:

   ```bash
   docker compose up -d neo4j
   ```

   Tarda unos segundos en aceptar conexiones. El navegador queda en
   <http://localhost:7474>, con usuario `neo4j` y la contraseña del
   `compose.yaml`.

4. Instala las dependencias y comprueba que todo arranca:

   ```bash
   uv sync
   uv run python -m pytest -q
   ```

Al principio fallan casi todas: eso es lo normal, la carga y las siete
consultas están por implementar.

## Qué hay aquí

| Fichero | Qué es |
|---|---|
| `carga.py` | La construcción del grafo, con los `TODO` |
| `consultas.py` | Las siete consultas G1 … G7, con los `TODO` |
| `datos/` | Los cinco ficheros NDJSON: los cuatro de la fase 2, con `id_evento` en los eventos, y `asistencia.json` |
| `pyproject.toml` | Las dependencias. No hace falta tocarlo |
| `carga_test.py` | Las pruebas de la carga |
| `modelo_test.py` | Las pruebas de los requisitos del modelo |
| `consultas_test.py` | Las pruebas de las consultas |
| `conftest.py` | La conexión a Neo4j que usan las pruebas. **No lo edites** |

## Las pruebas vacían el grafo

Neo4j Community, que es la edición del `compose.yaml`, solo tiene una base de
datos. Las pruebas la **borran** —nodos, relaciones, restricciones e índices— y
la recargan con tu carga en cada ejecución, así que lo que hayas creado a mano
en el navegador se pierde. Si quieres conservar algo, guárdalo como consulta en
un fichero, no en la base.

Borran también las restricciones porque sobreviven a un `DETACH DELETE`: si
cambias de modelo, una restricción del diseño anterior podría hacer fallar la
carga nueva. Si pruebas a mano en el navegador, tenlo en cuenta (`SHOW
CONSTRAINTS` las enseña).

Para tener el grafo cargado y probar las consultas a mano en el navegador,
cuando tu `carga.py` ya funcione:

```bash
uv run python -c "
from neo4j import GraphDatabase
import carga
with GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'abd-local-2026')) as d:
    print(carga.carga_grafo(d, 'datos'))
"
```

## Qué se ve al ejecutar las pruebas

Cuando todo está bien, un punto por prueba:

```
....................................                                     [100%]
39 passed in 6.1s
```

Mientras no lo esté, cada `F` es una prueba que falla, y abajo sale el nombre
de cada una con el motivo:

```
FAILED carga_test.py::test_la_carga_es_idempotente - AssertionError: la segunda carga ha cambiado las relaciones
1 failed, 38 passed in 6.3s
```

Las pruebas del modelo y de las consultas usan **tu** `carga.py` para construir
el grafo, así que mientras la carga no funcione fallarán también. Empieza por
ella.

Para trabajar sobre una parte:

```bash
uv run python -m pytest carga_test.py -q
uv run python -m pytest modelo_test.py -v
uv run python -m pytest consultas_test.py -k g5 -v
uv run python -m pytest -x --tb=short      # para en el primer fallo
```

## Qué exige cada prueba

| Prueba | Qué tiene que funcionar |
|---|---|
| `test_carga_devuelve_el_resumen` | `carga_grafo` devuelve los documentos procesados de cada fichero |
| `test_la_carga_crea_nodos_y_relaciones` | El grafo no queda vacío |
| `test_la_carga_es_idempotente` | Cargar dos veces deja los mismos nodos de cada etiqueta y las mismas relaciones de cada tipo que cargar una |
| `test_las_fechas_son_temporales` | Hay fechas de tipo temporal y ninguna guardada como texto |
| `test_vacia_el_grafo` | `vacia_grafo` no deja ningún nodo |
| `test_cada_entidad_tiene_su_clave` | Cada recinto, artista, evento y asistente es un nodo con su clave, y la clave tiene restricción de unicidad |
| `test_todo_nodo_tiene_restriccion_de_unicidad` | Ningún nodo se queda sin restricción de unicidad en alguna de sus etiquetas |
| `test_cada_clave_esta_en_un_solo_sitio` | El valor de una clave no aparece copiado como propiedad en otro nodo ni en una relación |
| `test_no_hay_nodos_sueltos` | Todo nodo tiene al menos una relación |
| `test_estan_las_siete_consultas` | `CONSULTAS` tiene exactamente G1 … G7 |
| `test_forma_del_contrato[G1…G7]` | Cada consulta tiene su Cypher no vacío y sus parámetros |
| `test_los_parametros_no_estan_interpolados[G1…G7]` | Los valores van en `params`, no escritos dentro del Cypher |
| `test_la_consulta_se_ejecuta[G1…G7]` | Neo4j ejecuta la consulta sin error |
| `test_g1_coasistencia` | Seis personas, ordenadas, con su ciudad y sin Ana |
| `test_g2_colaboraciones` | Seis parejas, cada una en un solo sentido |
| `test_g3_eventos_perdidos` | Los diez primeros, ordenados |
| `test_g4_terceros_a_n_saltos` | Con `saltos=2`, nadie a más de dos saltos y orden por saltos |
| `test_g5_camino_entre_generos` | Una sola fila, de `jazz` a `electrónica`, con un artista entre cada dos géneros |
| `test_g5_generos_aislados_no_dan_camino` | Entre dos géneros sin camino, cero filas y ningún error |
| `test_g6_camino_entre_asistentes` | Una sola fila, de Iker a Andrés, con un evento entre cada dos personas |
| `test_g7_artistas_recomendados` | Ordenados, con los géneros ordenados y sin artistas que Ana ya ha visto |

## Lo que estas pruebas no dicen

Pasarlas es **necesario, pero no suficiente**:

- Como el modelo es vuestro, no saben qué etiquetas ni qué relaciones habéis
  elegido: comprueban los requisitos del modelo que cumple cualquier diseño
  correcto, no si el vuestro es bueno.
- De las consultas comprueban la forma y algunos valores concretos, no el
  resultado entero. La corrección compara el resultado **completo** de cada
  consulta —columnas, valores, listas y orden— con el de la solución de
  referencia.
- La calidad del modelo (1 punto) se valora aparte, a partir del esquema de
  vuestro grafo: lo que dice el enunciado sobre nombres, sentido de las
  relaciones y redundancia.

La corrección ejecuta las consultas **sobre el grafo que construye tu
`carga.py`**, igual que estas pruebas: un error en la carga se nota también en
las consultas que pasan por esa parte del grafo.

Lo que sí es buena noticia: se comparan **resultados, no formas**. Cualquier
modelo y cualquier Cypher que produzcan la salida pedida puntúan igual.

## Tres cosas que no hay que cambiar

- Los nombres de los ficheros: las pruebas hacen `import carga` y
  `from consultas import CONSULTAS`.
- Las firmas de `carga.py`: `crea_restricciones(driver)`,
  `carga_grafo(driver, directorio)` y `vacia_grafo(driver)`.
- El diccionario `CONSULTAS` del final de `consultas.py`: es el contrato con el
  que se corrige. Lo que se rellena son las cadenas `G1` … `G7`.

Los ficheros de `datos/` tampoco se modifican: la corrección usa exactamente
estos datos.

## La entrega

Tu repositorio es para trabajar. La entrega es la que dice el enunciado: un
**ZIP** con la carpeta del proyecto y estos tres ficheros —`carga.py`,
`consultas.py` y `pyproject.toml`— nombrado
`P4_G<grupo>_Nombre_Apellido-Nombre_Apellido.zip`.

## Si algo no arranca

El manual **Entorno de trabajo** de la asignatura tiene la tabla de errores
frecuentes. Los más habituales aquí:

- `ServiceUnavailable` → Neo4j no está levantado, o todavía está arrancando:
  `docker compose up -d neo4j` y espera unos segundos.
- `AuthError` → la contraseña no es la del `compose.yaml`. Si cambiaste la
  contraseña en el navegador, las pruebas la leen de la variable
  `NEO4J_PASSWORD`.
- `ModuleNotFoundError: No module named 'carga'` → ejecutaste `pytest` a
  secas. Tiene que ser `python -m pytest`, desde la carpeta del proyecto.
- `NotImplementedError` → es el `raise` del esqueleto: esa función todavía
  está por hacer.
