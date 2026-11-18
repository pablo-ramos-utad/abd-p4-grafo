"""EnVivo · fase 4 · construcción del grafo.

Hay que implementar la carga del grafo a partir de los ficheros NDJSON de
`datos/`, con el modelo que hayáis diseñado. Las firmas **no deben cambiarse**:
son el contrato de corrección.

**Requisito central: la carga debe ser idempotente.** Ejecutarla dos veces tiene
que dejar el grafo igual que ejecutarla una, de modo que un script que falle a
mitad se pueda relanzar sin duplicar nada.
"""

import json
from pathlib import Path

from neo4j import Driver

COLECCIONES = ["recinto", "artista", "evento", "asistente", "asistencia"]


def lee_ndjson(directorio: Path, nombre: str) -> list[dict]:
    """Lee un fichero NDJSON: un documento JSON por línea."""
    ruta = Path(directorio) / f"{nombre}.json"
    return [
        json.loads(linea)
        for linea in ruta.read_text(encoding="utf-8").splitlines()
        if linea.strip()
    ]


def crea_restricciones(driver: Driver) -> None:
    """Crea las restricciones de unicidad del modelo.

    Todo nodo del grafo tiene que tener una etiqueta con restricción de
    unicidad sobre su clave.
    """
    # TODO
    raise NotImplementedError


def carga_grafo(driver: Driver, directorio: str | Path = "datos") -> dict[str, int]:
    """Construye el grafo completo y devuelve cuántas filas ha procesado.

    El valor de retorno es un diccionario `{"recinto": 6, "artista": 12, ...}`
    con una entrada por colección.

    Las fechas vienen en Extended JSON (`{"$date": "..."}`) y se almacenan
    como tipo temporal, no como texto.
    """
    # TODO
    raise NotImplementedError


def vacia_grafo(driver: Driver) -> None:
    """Borra todos los nodos y relaciones del grafo."""
    # TODO
    raise NotImplementedError
