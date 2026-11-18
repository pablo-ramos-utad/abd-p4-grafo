"""Pruebas visibles · requisitos del modelo del grafo.

    uv run python -m pytest modelo_test.py -q

El modelo no se entrega aparte: se deduce del grafo que construye tu carga.
Estas pruebas no saben qué etiquetas ni qué relaciones has elegido; comprueban
tres requisitos que cualquier modelo correcto cumple:

- cada recinto, artista, evento y asistente es un nodo, identificado por su
  clave, con restricción de unicidad; y todo nodo tiene alguna restricción;
- el valor de cada clave está en un solo sitio del grafo: el nodo al que
  identifica;
- no hay nodos sin relaciones.
"""

import json

#: Clave de cada colección que es una entidad, y por la que la referencian
#: las demás.
CLAVES = {"recinto": "nombre", "artista": "nombre", "evento": "id_evento", "asistente": "email"}


def _dominios(datos):
    res = {}
    for coleccion, clave in CLAVES.items():
        lineas = (datos / f"{coleccion}.json").read_text(encoding="utf-8").splitlines()
        res[f"{coleccion}.{clave}"] = {json.loads(l)[clave] for l in lineas if l.strip()}
    return res


def _ubicaciones(sesion):
    """Cada propiedad del grafo con los textos que guarda y cuántos elementos
    la tienen."""
    res = {}
    for tipo, consulta in [
        ("nodo", "MATCH (n) UNWIND keys(n) AS k RETURN labels(n) AS donde, k, collect(n[k]) AS vs"),
        ("rel", "MATCH ()-[r]->() UNWIND keys(r) AS k RETURN type(r) AS donde, k, collect(r[k]) AS vs"),
    ]:
        for r in sesion.run(consulta):
            donde = tuple(sorted(r["donde"])) if tipo == "nodo" else r["donde"]
            planos = [x for v in r["vs"] for x in (v if isinstance(v, list) else [v])]
            textos = [x for x in planos if isinstance(x, str)]
            res[(tipo, donde, r["k"])] = {"textos": set(textos), "lista": textos, "n": len(r["vs"])}
    return res


def _restricciones(sesion):
    return {
        (et, tuple(r["properties"]))
        for r in sesion.run("SHOW CONSTRAINTS YIELD type, entityType, labelsOrTypes, properties")
        if r["entityType"] == "NODE" and r["type"] in ("UNIQUENESS", "NODE_KEY")
        for et in r["labelsOrTypes"]
    }


def _nombre(u):
    tipo, donde, prop = u
    return f"(:{':'.join(donde)}).{prop}" if tipo == "nodo" else f"[:{donde}].{prop}"


def test_cada_entidad_tiene_su_clave(grafo_solo_lectura, datos):
    sesion, _ = grafo_solo_lectura
    ubic, restr = _ubicaciones(sesion), _restricciones(sesion)
    problemas = []
    for nombre, dominio in _dominios(datos).items():
        prop = nombre.split(".")[1]
        candidatas = [
            u for u, v in ubic.items()
            if u[0] == "nodo" and u[2] == prop and v["textos"] == dominio
            and v["n"] == len(dominio) and len(v["lista"]) == len(dominio)
        ]
        if not candidatas:
            problemas.append(f"{nombre}: no hay un nodo por documento con su `{prop}`")
        elif not any((et, (prop,)) in restr for et in candidatas[0][1]):
            problemas.append(f"{nombre}: {_nombre(candidatas[0])} no tiene restricción de unicidad")
    assert not problemas, "\n".join(problemas)


def test_todo_nodo_tiene_restriccion_de_unicidad(grafo_solo_lectura):
    sesion, _ = grafo_solo_lectura
    con = {et for et, _ in _restricciones(sesion)}
    sin = [r["e"] for r in sesion.run("MATCH (n) RETURN DISTINCT labels(n) AS e")
           if not set(r["e"]) & con]
    assert not sin, f"hay nodos sin restricción de unicidad: {sin}"


def test_cada_clave_esta_en_un_solo_sitio(grafo_solo_lectura, datos):
    """Si el valor de una clave aparece también como propiedad de otro nodo o
    de una relación, es una referencia que debería ser una relación."""
    sesion, _ = grafo_solo_lectura
    ubic = _ubicaciones(sesion)
    problemas = []
    for nombre, dominio in _dominios(datos).items():
        sitios = [u for u, v in ubic.items() if len(v["textos"] & dominio) >= 2]
        if len(sitios) > 1:
            problemas.append(f"{nombre} está en {len(sitios)} sitios: "
                             + ", ".join(sorted(_nombre(s) for s in sitios)))
    assert not problemas, "\n".join(problemas)


def test_no_hay_nodos_sueltos(grafo_solo_lectura):
    sesion, _ = grafo_solo_lectura
    sueltos = [f"{r['n']} (:{':'.join(r['e'])})" for r in sesion.run(
        "MATCH (n) WHERE NOT (n)--() RETURN labels(n) AS e, count(*) AS n")]
    assert not sueltos, f"nodos sin ninguna relación: {sueltos}"
