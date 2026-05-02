"""BSP (Binary Space Partitioning) - eliminacja zaslonietych powierzchni."""
from algebra import vec3_sub, vec3_dot, vec3_cross, vec3_normalize


EPSILON = 1e-5   # tolerancja numeryczna dla klasyfikacji punktow

FRONT = 1
BACK = -1
COPLANAR = 0
SPANNING = 2


class Polygon:
    """Wielokat 3D z wyliczona normalna i plaszczyzna (do BSP)."""
    def __init__(self, vertices, color="white"):
        self.vertices = vertices  # [[x, y, z], ...] - min. 3 punkty
        self.color = color
        # Wyznacz normalna i odleglosc d plaszczyzny (rownanie: N*P + d = 0)
        self.normal = [0, 0, 0]
        self.d = 0.0
        if len(vertices) >= 3:
            edge1 = vec3_sub(vertices[1], vertices[0])
            edge2 = vec3_sub(vertices[2], vertices[0])
            self.normal = vec3_normalize(vec3_cross(edge1, edge2))
            self.d = -vec3_dot(self.normal, vertices[0])


def classify_point(normal, d, point):
    """Klasyfikuj punkt wzgledem plaszczyzny: FRONT, BACK lub COPLANAR."""
    dist = vec3_dot(normal, point) + d
    if dist > EPSILON:
        return FRONT
    elif dist < -EPSILON:
        return BACK
    return COPLANAR


def classify_polygon(splitter, poly):
    """Klasyfikuj wielokat wzgledem plaszczyzny splittera."""
    front_count = 0
    back_count = 0
    for v in poly.vertices:
        c = classify_point(splitter.normal, splitter.d, v)
        if c == FRONT:
            front_count += 1
        elif c == BACK:
            back_count += 1
    if front_count > 0 and back_count > 0:
        return SPANNING
    if front_count > 0:
        return FRONT
    if back_count > 0:
        return BACK
    return COPLANAR


def split_polygon(splitter_normal, splitter_d, poly):
    """Podziel wielokat na czesc przednia i tylna wzgledem plaszczyzny.
    Zwraca (front_poly, back_poly) jako obiekty Polygon."""
    front_verts = []
    back_verts = []
    verts = poly.vertices
    n = len(verts)

    for i in range(n):
        j = (i + 1) % n
        vi = verts[i]
        vj = verts[j]
        ci = classify_point(splitter_normal, splitter_d, vi)
        cj = classify_point(splitter_normal, splitter_d, vj)

        if ci != BACK:
            front_verts.append(vi)
        if ci != FRONT:
            back_verts.append(vi)

        if (ci == FRONT and cj == BACK) or (ci == BACK and cj == FRONT):
            # Punkt przeciecia krawedzi z plaszczyzna
            edge = vec3_sub(vj, vi)
            denom = vec3_dot(splitter_normal, edge)
            if abs(denom) > 1e-12:
                t = -(vec3_dot(splitter_normal, vi) + splitter_d) / denom
                t = max(0.0, min(1.0, t))
                intersection = [
                    vi[0] + t * edge[0],
                    vi[1] + t * edge[1],
                    vi[2] + t * edge[2],
                ]
                front_verts.append(intersection)
                back_verts.append(intersection)

    front_poly = None
    back_poly = None
    if len(front_verts) >= 3:
        front_poly = Polygon(front_verts, poly.color)
        # Zachowaj oryginalna normalna (nie przeliczaj z nowych wierzcholkow)
        front_poly.normal = list(poly.normal)
        front_poly.d = poly.d
    if len(back_verts) >= 3:
        back_poly = Polygon(back_verts, poly.color)
        back_poly.normal = list(poly.normal)
        back_poly.d = poly.d
    return front_poly, back_poly


class BSPNode:
    """Wezel drzewa BSP."""
    def __init__(self):
        self.polygon = None     # wielokat definiujacy plaszczyzne podzialu
        self.coplanar = []      # wielokaty lezace w tej samej plaszczyznie
        self.front = None       # poddrzewo - strona przednia
        self.back = None        # poddrzewo - strona tylna


def build_bsp_tree(polygons):
    """Budowanie drzewa BSP z listy wielokatow (rekurencyjne)."""
    if not polygons:
        return None

    node = BSPNode()
    # Wybieramy pierwszy wielokat jako splitter (plaszczyzne podzialu)
    node.polygon = polygons[0]
    node.coplanar = [polygons[0]]

    front_list = []
    back_list = []

    for poly in polygons[1:]:
        classification = classify_polygon(node.polygon, poly)
        if classification == COPLANAR:
            node.coplanar.append(poly)
        elif classification == FRONT:
            front_list.append(poly)
        elif classification == BACK:
            back_list.append(poly)
        elif classification == SPANNING:
            f, b = split_polygon(node.polygon.normal, node.polygon.d, poly)
            if f:
                front_list.append(f)
            if b:
                back_list.append(b)

    node.front = build_bsp_tree(front_list)
    node.back = build_bsp_tree(back_list)
    return node


def traverse_bsp(node, camera_pos, result):
    """Przejscie drzewa BSP w kolejnosci back-to-front (algorytm malarza).
    Wielokaty dalsze od kamery trafiaja do listy wczesniej - beda rysowane pierwsze."""
    if node is None:
        return

    # Sprawdz po ktorej stronie plaszczyzny podzialu lezy kamera
    side = classify_point(node.polygon.normal, node.polygon.d, camera_pos)

    if side == FRONT:
        # Kamera po stronie przedniej: rysuj najpierw tyl, potem node, potem przod
        traverse_bsp(node.back, camera_pos, result)
        result.extend(node.coplanar)
        traverse_bsp(node.front, camera_pos, result)
    else:
        # Kamera po stronie tylnej (lub w plaszczyznie): odwrotnie
        traverse_bsp(node.front, camera_pos, result)
        result.extend(node.coplanar)
        traverse_bsp(node.back, camera_pos, result)


def meshes_to_polygons(meshes):
    """Konwertuj liste siatek (z faces) na liste wielokatow Polygon."""
    polygons = []
    for mesh in meshes:
        for face in mesh.faces:
            verts = [list(mesh.vertices[i]) for i in face]
            polygons.append(Polygon(verts, mesh.color))
    return polygons
