"""Pruebas visibles · consultas sobre el grafo.

    uv run python -m pytest consultas_test.py -q
"""

import pytest

from consultas import CONSULTAS

IDS = ["G1", "G2", "G3", "G4", "G5", "G6", "G7"]


@pytest.fixture
def ejecuta(grafo_solo_lectura):
    sesion, _ = grafo_solo_lectura

    def _ejecuta(cid):
        c = CONSULTAS[cid]
        return [dict(r) for r in sesion.run(c["cypher"], **c["params"])]

    return _ejecuta


# ── El contrato de entrega ──────────────────────────────────────────────────

def test_estan_las_siete_consultas():
    assert sorted(CONSULTAS) == IDS


@pytest.mark.parametrize("cid", IDS)
def test_forma_del_contrato(cid):
    c = CONSULTAS[cid]
    assert "cypher" in c and "params" in c
    assert isinstance(c["cypher"], str) and c["cypher"].strip(), f"{cid}: Cypher vacío"
    assert isinstance(c["params"], dict)


@pytest.mark.parametrize("cid", IDS)
def test_los_parametros_no_estan_interpolados(cid):
    """Los valores van en params, no incrustados en el texto."""
    c = CONSULTAS[cid]
    for valor in c["params"].values():
        if isinstance(valor, str):
            assert valor not in c["cypher"], (
                f"{cid}: el valor '{valor}' aparece en el texto de la consulta; "
                "tiene que pasarse como parámetro"
            )


@pytest.mark.parametrize("cid", IDS)
def test_la_consulta_se_ejecuta(cid, ejecuta):
    ejecuta(cid)


# ── Resultados concretos ────────────────────────────────────────────────────

def test_g1_coasistencia(ejecuta):
    filas = ejecuta("G1")
    assert len(filas) == 6, "Ana Torres ha coincidido con seis personas"
    assert filas[0]["eventos_juntos"] == 6
    juntos = [f["eventos_juntos"] for f in filas]
    assert juntos == sorted(juntos, reverse=True), "ordenado descendente"
    assert all("ciudad" in f for f in filas)
    assert "Ana Torres" not in [f["persona"] for f in filas], \
        "no debe aparecer ella misma"


def test_g2_colaboraciones(ejecuta):
    filas = ejecuta("G2")
    assert len(filas) == 6, "hay seis parejas de artistas que han compartido cartel"
    parejas = {(f["artista_a"], f["artista_b"]) for f in filas}
    assert len(parejas) == 6, "cada pareja una sola vez, no una por sentido"
    for a, b in parejas:
        assert (b, a) not in parejas, f"la pareja {a}/{b} sale en los dos sentidos"
    assert all(f["un_ejemplo"] for f in filas)


def test_g3_eventos_perdidos(ejecuta):
    filas = ejecuta("G3")
    assert len(filas) == 10, "se piden los diez primeros"
    assert filas[0]["coasistentes_que_fueron"] == 3
    valores = [f["coasistentes_que_fueron"] for f in filas]
    assert valores == sorted(valores, reverse=True)


def test_g4_terceros_a_n_saltos(ejecuta):
    filas = ejecuta("G4")
    assert filas, "debería haber terceros alcanzables"
    assert all(f["saltos"] <= 2 for f in filas), \
        "con saltos=2 no puede haber resultados a más distancia"
    assert all(f["tercero"] != "Ana Torres" for f in filas)
    saltos = [f["saltos"] for f in filas]
    assert saltos == sorted(saltos), "ordenado por saltos ascendente"


def test_g5_camino_entre_generos(ejecuta):
    filas = ejecuta("G5")
    assert len(filas) == 1
    fila = filas[0]
    assert fila["generos"][0] == "jazz" and fila["generos"][-1] == "electrónica"
    assert fila["saltos_de_genero"] == len(fila["generos"]) - 1
    assert len(fila["artistas_puente"]) == fila["saltos_de_genero"], \
        "entre cada par de géneros consecutivos hay un artista"


def test_g5_generos_aislados_no_dan_camino(grafo_solo_lectura):
    """Dos géneros del grafo están aislados: la consulta no falla, no devuelve."""
    sesion, _ = grafo_solo_lectura
    c = CONSULTAS["G5"]
    filas = list(sesion.run(c["cypher"], desde="clásica", hasta="rock"))
    assert filas == [], "sin camino, cero filas y ningún error"


def test_g6_camino_entre_asistentes(ejecuta):
    filas = ejecuta("G6")
    assert len(filas) == 1
    fila = filas[0]
    assert fila["personas"][0] == "Iker Larrañaga"
    assert fila["personas"][-1] == "Andrés Vila"
    assert fila["saltos"] == len(fila["personas"]) - 1
    assert len(fila["eventos_puente"]) == fila["saltos"], \
        "entre cada par de personas consecutivas hay un evento"


def test_g7_artistas_recomendados(ejecuta):
    filas = ejecuta("G7")
    assert filas, "debería recomendar algún artista"
    assert filas[0]["coasistentes"] == 3
    valores = [f["coasistentes"] for f in filas]
    assert valores == sorted(valores, reverse=True)
    for f in filas:
        assert f["generos"] == sorted(f["generos"]), "los géneros vienen ordenados"
    assert "Vetusta Morla" not in [f["artista"] for f in filas], \
        "Ana ya ha visto a Vetusta Morla: no se le puede recomendar"
