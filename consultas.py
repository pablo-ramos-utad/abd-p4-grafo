"""EnVivo · fase 4 · consultas sobre el grafo.

Cada consulta es una cadena de Cypher con sus parámetros aparte. **Nunca se
interpola nada en el texto**: los valores van en `params` y el driver los envía
por separado, que es lo que evita la inyección y lo que permite que Neo4j
reutilice el plan de la consulta.

    from consultas import CONSULTAS
    c = CONSULTAS["G1"]
    with driver.session() as s:
        filas = [dict(r) for r in s.run(c["cypher"], **c["params"])]

El diccionario `CONSULTAS` del final ya está escrito y **no debe modificarse**:
es el contrato de corrección.
"""

# ── G1 · Con quién ha coincidido ────────────────────────────────────────────
# Dos personas coinciden si han asistido al mismo evento.
# Devuelve: persona, ciudad, eventos_juntos
# Orden: eventos_juntos descendente y, a igualdad, persona ascendente.
G1 = """
// TODO
"""

# ── G2 · Artistas que han compartido cartel ─────────────────────────────────
# Devuelve: artista_a, artista_b, eventos_juntos, un_ejemplo (un título)
# Cada pareja debe salir UNA sola vez, no una por sentido.
# Orden: eventos_juntos descendente, luego artista_a y artista_b ascendentes.
G2 = """
// TODO
"""

# ── G3 · Eventos que se perdió pero vieron sus co-asistentes ────────────────
# Eventos a los que la persona NO asistió pero sí alguien con quien ha
# coincidido. Devuelve: evento, coasistentes_que_fueron. Los diez primeros.
# Orden: coasistentes_que_fueron descendente y, a igualdad, evento ascendente.
G3 = """
// TODO
"""

# ── G4 · Terceros alcanzables en 1..N saltos de co-asistencia ───────────────
# Personas que NO han coincidido con la persona dada, pero sí están a entre 1 y
# N saltos de co-asistencia de alguien con quien ella sí ha coincidido.
# Devuelve: intermedio, tercero, saltos (el mínimo).
# Orden: saltos ascendente, luego intermedio y tercero ascendentes.
#
# N es el parámetro $saltos, de 3 como máximo. Con N = 3 la consulta tiene que
# responder en menos de 5 segundos.
G4 = """
// TODO
"""

# ── G5 · Camino de influencia entre dos géneros ─────────────────────────────
# Camino más corto entre dos géneros, pasando por artistas que pertenecen a
# ambos. Devuelve: generos (lista), artistas_puente (lista), saltos_de_genero.
#
# Hay varios caminos igual de cortos: devuelve UNA sola fila, la del camino que
# va primero al ordenar por artistas_puente.
#
# Si los dos géneros no están conectados, la consulta no devuelve filas. Eso es
# correcto: hay dos géneros aislados en el grafo.
G5 = """
// TODO
"""

# ── G6 · Camino más corto entre dos asistentes ──────────────────────────────
# Por relaciones de co-asistencia. Devuelve: personas (lista de nombres),
# eventos_puente (lista de títulos), saltos.
#
# Hay varios caminos igual de cortos: devuelve UNA sola fila, la del camino que
# va primero al ordenar por eventos_puente.
G6 = """
// TODO
"""

# ── G7 · Artistas recomendados ──────────────────────────────────────────────
# Artistas que la persona NO ha visto nunca, pero sí han visto personas con las
# que ha coincidido. Devuelve: artista, coasistentes (cuántos co-asistentes lo
# han visto), eventos (en cuántos eventos distintos), generos (lista ORDENADA).
# Orden: coasistentes descendente, eventos descendente, artista ascendente.
G7 = """
// TODO
"""


# ── Contrato de entrega · no modificar ──────────────────────────────────────
CONSULTAS = {
    "G1": {"cypher": G1, "params": {"email": "ana.torres@example.com"},
           "descripcion": "Con quién ha coincidido Ana Torres"},
    "G2": {"cypher": G2, "params": {},
           "descripcion": "Artistas que han compartido cartel"},
    "G3": {"cypher": G3, "params": {"email": "ana.torres@example.com"},
           "descripcion": "Eventos que se perdió pero vieron sus co-asistentes"},
    "G4": {"cypher": G4, "params": {"email": "ana.torres@example.com", "saltos": 2},
           "descripcion": "Terceros alcanzables en 1..N saltos de co-asistencia"},
    "G5": {"cypher": G5, "params": {"desde": "jazz", "hasta": "electrónica"},
           "descripcion": "Camino de influencia entre dos géneros"},
    "G6": {"cypher": G6, "params": {"desde": "iker.larranaga@example.com",
                                    "hasta": "andres.vila@example.com"},
           "descripcion": "Camino más corto entre dos asistentes"},
    "G7": {"cypher": G7, "params": {"email": "ana.torres@example.com"},
           "descripcion": "Artistas recomendados a Ana Torres"},
}
