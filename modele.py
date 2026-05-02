"""Modele 3D - wielosciany, siatka podlogi, osie."""
from algebra import vec3_sub, vec3_dot, vec3_cross, vec3_normalize


class Mesh:
    """Wieloscian: wierzcholki + krawedzie + sciany (faces)."""
    def __init__(self, vertices, edges, color="white", faces=None):
        self.vertices = vertices   # [[x, y, z], ...]
        self.edges = edges         # [(i, j), ...]
        self.faces = faces or []   # [[i, j, k, ...], ...] - indeksy wierzcholkow
        self.color = color


def make_cube(cx, cy, cz, size, color="white"):
    s = size / 2
    v = [
        [cx + a * s, cy + b * s, cz + c * s]
        for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)
    ]
    # 0(-,-,-) 1(-,-,+) 2(-,+,-) 3(-,+,+)
    # 4(+,-,-) 5(+,-,+) 6(+,+,-) 7(+,+,+)
    e = [
        (0, 1), (0, 2), (0, 4),
        (1, 3), (1, 5),
        (2, 3), (2, 6),
        (3, 7),
        (4, 5), (4, 6),
        (5, 7), (6, 7),
    ]
    # Sciany szescianu (kolejnosc wierzcholkow - normalna na zewnatrz)
    faces = [
        [1, 3, 2, 0],  # lewa  (-X)
        [6, 7, 5, 4],  # prawa (+X)
        [4, 5, 1, 0],  # dol   (-Y)
        [3, 7, 6, 2],  # gora  (+Y)
        [2, 6, 4, 0],  # tyl   (-Z)
        [5, 7, 3, 1],  # przod (+Z)
    ]
    return Mesh(v, e, color, faces)


def make_pyramid(cx, cy, cz, base, height, color="yellow"):
    s = base / 2
    v = [
        [cx - s, cy, cz - s],
        [cx + s, cy, cz - s],
        [cx + s, cy, cz + s],
        [cx - s, cy, cz + s],
        [cx, cy + height, cz],
    ]
    e = [(0, 1), (1, 2), (2, 3), (3, 0),
         (0, 4), (1, 4), (2, 4), (3, 4)]
    faces = [
        [0, 1, 2, 3],  # podstawa (normalna w dol)
        [1, 0, 4],     # sciana przednia (normalna na zewnatrz)
        [2, 1, 4],     # sciana prawa
        [3, 2, 4],     # sciana tylna
        [0, 3, 4],     # sciana lewa
    ]
    return Mesh(v, e, color, faces)


def make_octahedron(cx, cy, cz, size, color="red"):
    s = size
    v = [
        [cx + s, cy, cz], [cx - s, cy, cz],
        [cx, cy + s, cz], [cx, cy - s, cz],
        [cx, cy, cz + s], [cx, cy, cz - s],
    ]
    e = [
        (0, 2), (0, 3), (0, 4), (0, 5),
        (1, 2), (1, 3), (1, 4), (1, 5),
        (2, 4), (2, 5), (3, 4), (3, 5),
    ]
    faces = [
        [0, 2, 4], [0, 4, 3], [0, 3, 5], [0, 5, 2],
        [1, 4, 2], [1, 3, 4], [1, 5, 3], [1, 2, 5],
    ]
    return Mesh(v, e, color, faces)


def make_grid(y, extent, step, color="#444444"):
    """Siatka podlogi (krawedzie wzdluz X i Z)."""
    verts, edges = [], []
    idx = 0
    for i in range(-extent, extent + 1, step):
        verts += [[i, y, -extent], [i, y, extent]]
        edges.append((idx, idx + 1))
        idx += 2
        verts += [[-extent, y, i], [extent, y, i]]
        edges.append((idx, idx + 1))
        idx += 2
    return Mesh(verts, edges, color)


def make_axes(length=15):
    """Osie XYZ jako trzy osobne siatki (R, G, B)."""
    return [
        Mesh([[0, 0, 0], [length, 0, 0]], [(0, 1)], "#ff4444"),
        Mesh([[0, 0, 0], [0, length, 0]], [(0, 1)], "#44ff44"),
        Mesh([[0, 0, 0], [0, 0, length]], [(0, 1)], "#4444ff"),
    ]
