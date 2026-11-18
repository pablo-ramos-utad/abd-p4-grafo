"""Pruebas visibles · construcción del grafo.

    uv run python -m pytest carga_test.py -q

El modelo del grafo lo diseñas tú, así que estas pruebas no saben qué etiquetas
ni qué relaciones has elegido: comprueban lo que cualquier carga correcta tiene
que cumplir. Las del diseño están en modelo_test.py.
"""

import re

from neo4j.time import Date, DateTime

RESUMEN = {"recinto": 6, "artista": 12, "evento": 32, "asistente": 15, "asistencia": 76}
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")


def _forma(sesion):
    """Nodos por combinación de etiquetas y relaciones por tipo."""
    nodos = {tuple(sorted(r["e"])): r["n"] for r in
             sesion.run("MATCH (n) RETURN labels(n) AS e, count(*) AS n")}
    rels = {r["t"]: r["n"] for r in
            sesion.run("MATCH ()-[r]->() RETURN type(r) AS t, count(*) AS n")}
    return nodos, rels


def _valores(sesion):
    consulta = ("MATCH (n) RETURN properties(n) AS p "
                "UNION ALL MATCH ()-[r]->() RETURN properties(r) AS p")
    for r in sesion.run(consulta):
        for v in r["p"].values():
            yield from (v if isinstance(v, list) else [v])


def test_carga_devuelve_el_resumen(grafo):
    _, resumen = grafo
    assert resumen == RESUMEN


def test_la_carga_crea_nodos_y_relaciones(grafo):
    sesion, _ = grafo
    nodos, rels = _forma(sesion)
    assert nodos, "la carga no ha creado ningún nodo"
    assert rels, "la carga no ha creado ninguna relación"


def test_la_carga_es_idempotente(grafo, driver, datos):
    """El requisito central: cargar dos veces deja el mismo grafo que una."""
    sesion, _ = grafo
    from conftest import _envuelve

    import carga
    antes = _forma(sesion)
    carga.carga_grafo(_envuelve(driver), datos)
    nodos, rels = _forma(sesion)

    assert nodos == antes[0], "la segunda carga ha cambiado los nodos"
    assert rels == antes[1], "la segunda carga ha cambiado las relaciones"


def test_las_fechas_son_temporales(grafo):
    sesion, _ = grafo
    valores = list(_valores(sesion))
    assert any(isinstance(v, (DateTime, Date)) for v in valores), \
        "no hay ninguna fecha guardada como tipo temporal"
    como_texto = [v for v in valores if isinstance(v, str) and ISO.match(v)]
    assert not como_texto, f"hay fechas guardadas como texto: {como_texto[:3]}"


def test_vacia_el_grafo(grafo, driver, sesion):
    import carga
    from conftest import _envuelve

    carga.vacia_grafo(_envuelve(driver))
    assert sesion.run("MATCH (n) RETURN count(n) AS n").single()["n"] == 0
