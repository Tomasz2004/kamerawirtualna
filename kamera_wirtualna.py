import tkinter as tk
import math


# ======================== Algebra macierzowa ========================

def mat4_identity():
    return [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]


def mat4_mul(a, b):
    """Mnozenie dwoch macierzy 4x4."""
    r = [[0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            s = 0
            for k in range(4):
                s += a[i][k] * b[k][j]
            r[i][j] = s
    return r


def mat4_vec(m, v):
    """Mnozenie macierzy 4x4 przez wektor [x, y, z, w]."""
    return [
        sum(m[i][j] * v[j] for j in range(4))
        for i in range(4)
    ]


def mat4_translation(tx, ty, tz):
    m = mat4_identity()
    m[0][3] = tx
    m[1][3] = ty
    m[2][3] = tz
    return m


def mat4_rot_x(angle):
    c, s = math.cos(angle), math.sin(angle)
    m = mat4_identity()
    m[1][1] = c;  m[1][2] = -s
    m[2][1] = s;  m[2][2] = c
    return m


def mat4_rot_y(angle):
    c, s = math.cos(angle), math.sin(angle)
    m = mat4_identity()
    m[0][0] = c;  m[0][2] = s
    m[2][0] = -s; m[2][2] = c
    return m


def mat4_rot_z(angle):
    c, s = math.cos(angle), math.sin(angle)
    m = mat4_identity()
    m[0][0] = c;  m[0][1] = -s
    m[1][0] = s;  m[1][1] = c
    return m


# ======================== Algebra wektorowa 3D ========================

def vec3_sub(a, b):
    """Roznica wektorow a - b."""
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def vec3_dot(a, b):
    """Iloczyn skalarny."""
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vec3_cross(a, b):
    """Iloczyn wektorowy."""
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def vec3_normalize(v):
    """Normalizacja wektora do dlugosci 1."""
    l = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if l < 1e-12:
        return [0, 0, 0]
    return [v[0] / l, v[1] / l, v[2] / l]


# ======================== Modele wieloscianow ========================

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
        [0, 2, 3, 1],  # lewa  (-X)
        [4, 5, 7, 6],  # prawa (+X)
        [0, 1, 5, 4],  # dol   (-Y)
        [2, 6, 7, 3],  # gora  (+Y)
        [0, 4, 6, 2],  # tyl   (-Z)
        [1, 3, 7, 5],  # przod (+Z)
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


# ======================== BSP (Binary Space Partitioning) ========================

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

    front_poly = Polygon(front_verts, poly.color) if len(front_verts) >= 3 else None
    back_poly = Polygon(back_verts, poly.color) if len(back_verts) >= 3 else None
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


# ======================== Kamera ========================

class Camera:
    def __init__(self):
        self.x, self.y, self.z = 0.0, 1.0, -8.0
        self.yaw = 0.0      # obrot wokol Y (lewo/prawo)
        self.pitch = 0.0     # obrot wokol X (gora/dol)
        self.roll = 0.0      # przechylenie wokol Z
        self.fov = 90.0      # pole widzenia w stopniach (zoom)

    def view_matrix(self):
        """Macierz widoku: swiat -> uklad kamery.
        V = Rz(-roll) * Rx(-pitch) * Ry(-yaw) * T(-pos)
        """
        t = mat4_translation(-self.x, -self.y, -self.z)
        m = mat4_mul(mat4_rot_y(-self.yaw), t)
        m = mat4_mul(mat4_rot_x(-self.pitch), m)
        m = mat4_mul(mat4_rot_z(-self.roll), m)
        return m

    def forward_vec(self):
        """Kierunek 'do przodu' kamery w ukladzie swiata."""
        cp = math.cos(self.pitch)
        sp = math.sin(self.pitch)
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)
        return [cp * sy, -sp, cp * cy]

    def right_vec(self):
        """Kierunek 'w prawo' kamery w ukladzie swiata (bez pitch)."""
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)
        return [cy, 0, -sy]

    def reset(self):
        self.x, self.y, self.z = 0.0, 1.0, -8.0
        self.yaw = self.pitch = self.roll = 0.0
        self.fov = 90.0


# ======================== Aplikacja ========================

class App:
    WIDTH = 900
    HEIGHT = 650
    MOVE_SPEED = 0.12
    ROT_SPEED = 0.025
    ZOOM_SPEED = 2.0

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kamera wirtualna - BSP hidden surface removal")
        self.canvas = tk.Canvas(
            self.root, width=self.WIDTH, height=self.HEIGHT, bg="black"
        )
        self.canvas.pack()

        self.cam = Camera()
        self.scene_meshes = self._build_scene()

        # Budujemy drzewo BSP ze scian (faces) obiektow
        solid_meshes = [m for m in self.scene_meshes if m.faces]
        self.polygons = meshes_to_polygons(solid_meshes)
        self.bsp_tree = build_bsp_tree(self.polygons)

        # Siatki bez scian (grid, osie) - rysowane jako wireframe
        self.wireframe_meshes = [m for m in self.scene_meshes if not m.faces]

        self.keys = set()
        self.root.bind("<KeyPress>",   lambda e: self.keys.add(e.keysym.lower()))
        self.root.bind("<KeyRelease>", lambda e: self.keys.discard(e.keysym.lower()))

        self._tick()
        self.root.mainloop()

    # --------------- budowa sceny ---------------

    def _build_scene(self):
        meshes = [
            make_cube(0, 0, 0, 2, "#00dddd"),
            make_cube(5, 0, 2, 1.5, "#00cc66"),
            make_cube(-4, 1, 6, 1.8, "#cc66ff"),
            make_pyramid(-2, -1.5, 3, 2, 3, "#ffcc00"),
            make_pyramid(1, -1.5, 8, 3, 2, "#ff88aa"),
            make_octahedron(3, 1.5, 5, 1.2, "#ff6644"),
            make_grid(-1.5, 10, 1, "#333333"),
        ]
        meshes += make_axes()
        return meshes

    # --------------- obsluga klawiatury ---------------

    def _handle_input(self):
        c = self.cam
        fwd = c.forward_vec()
        rgt = c.right_vec()
        m = self.MOVE_SPEED

        # Translacja w lokalnym ukladzie kamery
        if 'w' in self.keys:
            c.x += fwd[0] * m; c.y += fwd[1] * m; c.z += fwd[2] * m
        if 's' in self.keys:
            c.x -= fwd[0] * m; c.y -= fwd[1] * m; c.z -= fwd[2] * m
        if 'a' in self.keys:
            c.x -= rgt[0] * m; c.y -= rgt[1] * m; c.z -= rgt[2] * m
        if 'd' in self.keys:
            c.x += rgt[0] * m; c.y += rgt[1] * m; c.z += rgt[2] * m
        if 'q' in self.keys:
            c.y += m
        if 'e' in self.keys:
            c.y -= m

        # Obroty
        r = self.ROT_SPEED
        if 'left'  in self.keys: c.yaw   -= r
        if 'right' in self.keys: c.yaw   += r
        if 'up'    in self.keys: c.pitch -= r   # patrzenie w gore
        if 'down'  in self.keys: c.pitch += r   # patrzenie w dol
        if 'z'     in self.keys: c.roll  -= r
        if 'x'     in self.keys: c.roll  += r

        # Zoom (zmiana FOV)
        z = self.ZOOM_SPEED
        if 'plus' in self.keys or 'equal' in self.keys or 'kp_add' in self.keys:
            c.fov = max(10, c.fov - z)
        if 'minus' in self.keys or 'kp_subtract' in self.keys:
            c.fov = min(160, c.fov + z)

        # Reset kamery
        if 'r' in self.keys:
            c.reset()

    # --------------- renderowanie ---------------

    def _tick(self):
        self._handle_input()
        self._render()
        self.root.after(16, self._tick)

    def _project_point(self, point_cam, f, cx, cy, scale):
        """Rzutuj punkt z ukladu kamery na ekran. Zwraca (sx, sy) lub None."""
        if point_cam[2] <= 0.1:
            return None
        px = point_cam[0] * f / point_cam[2]
        py = point_cam[1] * f / point_cam[2]
        sx = cx + px * scale
        sy = cy - py * scale
        return (sx, sy)

    def _render(self):
        cv = self.canvas
        cv.delete("all")

        view = self.cam.view_matrix()
        f = 1.0 / math.tan(math.radians(self.cam.fov) / 2.0)

        cx = self.WIDTH / 2.0
        cy = self.HEIGHT / 2.0
        scale = min(cx, cy)

        # --- 1. Rysuj wireframe (siatka podlogi, osie) ---
        for mesh in self.wireframe_meshes:
            cam_verts = [
                mat4_vec(view, [v[0], v[1], v[2], 1.0])
                for v in mesh.vertices
            ]
            for i, j in mesh.edges:
                a = cam_verts[i]
                b = cam_verts[j]
                if a[2] <= 0.1 or b[2] <= 0.1:
                    continue
                x1 = a[0] * f / a[2]
                y1 = a[1] * f / a[2]
                x2 = b[0] * f / b[2]
                y2 = b[1] * f / b[2]
                sx1 = cx + x1 * scale
                sy1 = cy - y1 * scale
                sx2 = cx + x2 * scale
                sy2 = cy - y2 * scale
                cv.create_line(sx1, sy1, sx2, sy2, fill=mesh.color)

        # --- 2. BSP: przejscie back-to-front i rysowanie wypelnionych scian ---
        cam_pos = [self.cam.x, self.cam.y, self.cam.z]
        sorted_polys = []
        traverse_bsp(self.bsp_tree, cam_pos, sorted_polys)

        for poly in sorted_polys:
            # Transformacja wierzcholkow wielokata do ukladu kamery
            screen_pts = []
            all_visible = True
            for v in poly.vertices:
                cv_pt = mat4_vec(view, [v[0], v[1], v[2], 1.0])
                sp = self._project_point(cv_pt, f, cx, cy, scale)
                if sp is None:
                    all_visible = False
                    break
                screen_pts.append(sp)

            if not all_visible or len(screen_pts) < 3:
                continue

            # Rysuj wypelniony wielokat
            flat_pts = [coord for pt in screen_pts for coord in pt]

            # Ciemniejszy kolor wypelnienia, jasniejszy obwod
            cv.create_polygon(
                flat_pts,
                fill=self._darken_color(poly.color, 0.5),
                outline=poly.color,
                width=1,
            )

        # HUD - informacje o kamerze
        c = self.cam
        info = (
            f"Poz: ({c.x:.1f}, {c.y:.1f}, {c.z:.1f})   "
            f"Yaw: {math.degrees(c.yaw):.0f} deg   "
            f"Pitch: {math.degrees(c.pitch):.0f} deg   "
            f"Roll: {math.degrees(c.roll):.0f} deg   "
            f"FOV: {c.fov:.0f} deg"
        )
        cv.create_text(
            10, 10, anchor="nw", fill="white",
            font=("Consolas", 10), text=info,
        )
        cv.create_text(
            10, 28, anchor="nw", fill="#888888",
            font=("Consolas", 9),
            text="WASD=ruch  Q/E=gora/dol  "
                 "Strzalki=obrot  Z/X=przechylenie  "
                 "+/-=zoom  R=reset",
        )

    @staticmethod
    def _darken_color(hex_color, factor):
        """Przyciemnij kolor hex o dany wspolczynnik (0..1)."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(int(hex_color[0:2], 16) * factor)
            g = int(int(hex_color[2:4], 16) * factor)
            b = int(int(hex_color[4:6], 16) * factor)
            return f"#{r:02x}{g:02x}{b:02x}"
        return "#000000"


if __name__ == "__main__":
    App()
