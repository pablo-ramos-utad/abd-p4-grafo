"""Fixtures de la fase 4.

Las pruebas trabajan sobre la base de datos `envivopruebas` si el servidor
admite crearla. Con Neo4j Community, que solo tiene una, trabajan sobre la de
por omisión: la vacían, le quitan las restricciones y la recargan con tu carga.
"""

import os
from pathlib import Path

import pytest
from neo4j import GraphDatabase

URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
USUARIO = os.environ.get("NEO4J_USER", "neo4j")
PASSWORD = os.environ.get("NEO4J_PASSWORD", "abd-local-2026")
BD = os.environ.get("NEO4J_TEST_DB", "envivopruebas")


def _localiza_datos():
    """Busca el directorio datos/ junto a las pruebas o más arriba."""
    aqui = Path(__file__).resolve().parent
    for base in (aqui, *aqui.parents[:3]):
        candidato = base / "datos"
        if (candidato / "asistencia.json").exists():
            return candidato
    return aqui / "datos"


DATOS = _localiza_datos()


@pytest.fixture(scope="session")
def datos():
    if not (DATOS / "asistencia.json").exists():
        pytest.fail(f"No se encuentra {DATOS}. ¿Falta el directorio datos/?")
    return DATOS


@pytest.fixture(scope="session")
def driver():
    d = GraphDatabase.driver(URI, auth=(USUARIO, PASSWORD))
    d.verify_connectivity()
    # La edicion Community solo admite una base de datos, asi que si no se
    # puede crear otra se trabaja sobre la de por defecto.
    try:
        with d.session(database="system") as s:
            s.run(f"CREATE DATABASE {BD} IF NOT EXISTS WAIT").consume()
        base = BD
    except Exception:
        base = None
    d._abd_base = base
    yield d
    d.close()


@pytest.fixture
def sesion(driver):
    kwargs = {"database": driver._abd_base} if driver._abd_base else {}
    with driver.session(**kwargs) as s:
        yield s


def _limpia(sesion):
    """Borra nodos, restricciones e índices.

    Las restricciones sobreviven a un DETACH DELETE, y si cambias de modelo una
    restricción del diseño anterior puede hacer fallar la carga nueva.
    """
    sesion.run("MATCH (n) DETACH DELETE n").consume()
    for r in list(sesion.run("SHOW CONSTRAINTS YIELD name")):
        sesion.run(f"DROP CONSTRAINT `{r['name']}` IF EXISTS").consume()
    for r in list(sesion.run("SHOW INDEXES YIELD name, type WHERE type <> 'LOOKUP'")):
        sesion.run(f"DROP INDEX `{r['name']}` IF EXISTS").consume()


@pytest.fixture
def grafo(driver, datos, sesion):
    """Grafo recién cargado. Devuelve la sesión y el resumen de la carga.

    Ámbito de función: las pruebas de carga necesitan partir de cero y algunas
    modifican el grafo.
    """
    import carga

    # _limpia() espera con consume() a que el borrado se confirme. Sin eso, la
    # carga empieza en otra sesion antes de que termine y el borrado se lleva
    # nodos recien cargados: fallaba la primera ejecucion tras arrancar Neo4j.
    _limpia(sesion)
    resumen = carga.carga_grafo(_envuelve(driver), datos)
    return sesion, resumen


@pytest.fixture(scope="session")
def grafo_solo_lectura(driver, datos):
    """Grafo cargado una única vez, para las pruebas que no lo modifican.

    Recargarlo en cada prueba de consulta multiplicaba por diez el tiempo de la
    suite sin comprobar nada más.
    """
    import carga

    envuelto = _envuelve(driver)
    kwargs = {"database": driver._abd_base} if driver._abd_base else {}
    with driver.session(**kwargs) as s:
        _limpia(s)
    carga.carga_grafo(envuelto, datos)
    with driver.session(**kwargs) as s:
        yield s, None


def _envuelve(driver):
    """Driver que abre las sesiones en la base de datos de pruebas."""
    if driver._abd_base is None:
        return driver

    class _Driver:
        def __init__(self, real, base):
            self._real, self._base = real, base

        def session(self, **kwargs):
            kwargs.setdefault("database", self._base)
            return self._real.session(**kwargs)

        def __getattr__(self, nombre):
            return getattr(self._real, nombre)

    return _Driver(driver, driver._abd_base)
