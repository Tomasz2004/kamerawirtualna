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
    """Mnożenie dwóch macierzy 4×4."""
    r = [[0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            s = 0
            for k in range(4):
                s += a[i][k] * b[k][j]
            r[i][j] = s
    return r


def mat4_vec(m, v):
    """Mnożenie macierzy 4×4 przez wektor [x, y, z, w]."""
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


# ======================== Modele wielościanów ========================

class Mesh:
    """Wielościan krawędziowy: wierzchołki + lista krawędzi."""
    def __init__(self, vertices, edges, color="white"):
        self.vertices = vertices   # [[x, y, z], ...]
        self.edges = edges         # [(i, j), ...]
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
    return Mesh(v, e, color)


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
    return Mesh(v, e, color)


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
    return Mesh(v, e, color)


def make_grid(y, extent, step, color="#444444"):
    """Siatka podłogi (krawędzie wzdłuż X i Z)."""
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


# ======================== Kamera ========================

class Camera:
    def __init__(self):
        self.x, self.y, self.z = 0.0, 1.0, -8.0
        self.yaw = 0.0      # obrót wokół Y (lewo/prawo)
        self.pitch = 0.0     # obrót wokół X (góra/dół)
        self.roll = 0.0      # przechylenie wokół Z
        self.fov = 90.0      # pole widzenia w stopniach (zoom)

    def view_matrix(self):
        """Macierz widoku: świat → układ kamery.
        V = Rz(-roll) · Rx(-pitch) · Ry(-yaw) · T(-pos)
        """
        t = mat4_translation(-self.x, -self.y, -self.z)
        m = mat4_mul(mat4_rot_y(-self.yaw), t)
        m = mat4_mul(mat4_rot_x(-self.pitch), m)
        m = mat4_mul(mat4_rot_z(-self.roll), m)
        return m

    def forward_vec(self):
        """Kierunek 'do przodu' kamery w układzie świata."""
        cp = math.cos(self.pitch)
        sp = math.sin(self.pitch)
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)
        return [cp * sy, -sp, cp * cy]

    def right_vec(self):
        """Kierunek 'w prawo' kamery w układzie świata (bez pitch)."""
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
        self.root.title("Kamera wirtualna – wireframe")
        self.canvas = tk.Canvas(
            self.root, width=self.WIDTH, height=self.HEIGHT, bg="black"
        )
        self.canvas.pack()

        self.cam = Camera()
        self.scene = self._build_scene()

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

    # --------------- obsługa klawiatury ---------------

    def _handle_input(self):
        c = self.cam
        fwd = c.forward_vec()
        rgt = c.right_vec()
        m = self.MOVE_SPEED

        # Translacja w lokalnym układzie kamery
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
        if 'up'    in self.keys: c.pitch -= r   # patrzenie w górę
        if 'down'  in self.keys: c.pitch += r   # patrzenie w dół
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

    def _render(self):
        cv = self.canvas
        cv.delete("all")

        view = self.cam.view_matrix()
        f = 1.0 / math.tan(math.radians(self.cam.fov) / 2.0)

        cx = self.WIDTH / 2.0
        cy = self.HEIGHT / 2.0
        scale = min(cx, cy)

        for mesh in self.scene:
            # Transformacja wierzchołków do układu kamery
            cam_verts = [
                mat4_vec(view, [v[0], v[1], v[2], 1.0])
                for v in mesh.vertices
            ]

            for i, j in mesh.edges:
                a = cam_verts[i]
                b = cam_verts[j]

                # Pomijamy krawędzie z wierzchołkiem za kamerą (brak clippingu)
                if a[2] <= 0.1 or b[2] <= 0.1:
                    continue

                # Rzut perspektywiczny
                x1 = a[0] * f / a[2]
                y1 = a[1] * f / a[2]
                x2 = b[0] * f / b[2]
                y2 = b[1] * f / b[2]

                # Odwzorowanie na ekran (Y odwrócony)
                sx1 = cx + x1 * scale
                sy1 = cy - y1 * scale
                sx2 = cx + x2 * scale
                sy2 = cy - y2 * scale

                cv.create_line(sx1, sy1, sx2, sy2, fill=mesh.color)

        # HUD – informacje o kamerze
        c = self.cam
        info = (
            f"Poz: ({c.x:.1f}, {c.y:.1f}, {c.z:.1f})   "
            f"Yaw: {math.degrees(c.yaw):.0f}\u00b0   "
            f"Pitch: {math.degrees(c.pitch):.0f}\u00b0   "
            f"Roll: {math.degrees(c.roll):.0f}\u00b0   "
            f"FOV: {c.fov:.0f}\u00b0"
        )
        cv.create_text(
            10, 10, anchor="nw", fill="white",
            font=("Consolas", 10), text=info,
        )
        cv.create_text(
            10, 28, anchor="nw", fill="#888888",
            font=("Consolas", 9),
            text="WASD=ruch  Q/E=g\u00f3ra/d\u00f3\u0142  "
                 "Strza\u0142ki=obr\u00f3t  Z/X=przechylenie  "
                 "+/\u2013=zoom  R=reset",
        )


if __name__ == "__main__":
    App()
