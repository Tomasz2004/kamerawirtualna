"""Glowna aplikacja - okno, renderowanie, obsluga klawiatury."""
import tkinter as tk
import math

from algebra import mat4_vec
from modele import make_cube, make_pyramid, make_octahedron, make_grid, make_axes, make_sphere
from bsp import build_bsp_tree, traverse_bsp, meshes_to_polygons
from oswietlenie import PointLight, Material, phong_shading, hex_to_float, polygon_center
from kamera import Camera


class App:
    WIDTH = 900
    HEIGHT = 650
    MOVE_SPEED = 0.12
    ROT_SPEED = 0.025
    ZOOM_SPEED = 2.0

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kamera wirtualna - BSP + Phong")
        self.canvas = tk.Canvas(
            self.root, width=self.WIDTH, height=self.HEIGHT, bg="black"
        )
        self.canvas.pack()

        self.cam = Camera()
        self.scene_meshes = self._build_scene()

        # Punktowe zrodlo swiatla
        self.light = PointLight(
            position=[5.0, 8.0, -3.0],
            color=(1.0, 1.0, 0.95),
            intensity=1.0
        )
        # Material powierzchni (wspolny dla wszystkich obiektow)
        self.material = Material(
            ambient=0.15,
            diffuse=0.7,
            specular=0.4,
            shininess=32
        )

        # Budujemy drzewo BSP ze scian (faces) obiektow
        solid_meshes = [m for m in self.scene_meshes if m.faces]
        self.polygons = meshes_to_polygons(solid_meshes)
        self.bsp_tree = build_bsp_tree(self.polygons)

        # Siatki bez scian (grid, osie) - rysowane jako wireframe
        self.wireframe_meshes = [m for m in self.scene_meshes if not m.faces]

        self.stipple_on = False
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
            make_sphere(0, 2, -10, 1, 32, 30, "#00ffffp")
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
        if 'up'    in self.keys: c.pitch -= r
        if 'down'  in self.keys: c.pitch += r
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

        # POV z pozycji swiatla
        if 'l' in self.keys:
            self._set_camera_to_light()
            self.keys.discard('l')
        
        # Toggle stipple (przezroczystosc)
        if 't' in self.keys:
            self.stipple_on = not self.stipple_on
            self.keys.discard('t')

    def _set_camera_to_light(self):
        """Ustaw kamere na pozycji swiatla, patrzac w strone srodka sceny."""
        lp = self.light.position
        self.cam.x, self.cam.y, self.cam.z = lp[0], lp[1], lp[2]
        # Kierunek do srodka sceny (0,0,0)
        dx, dy, dz = -lp[0], -lp[1], -lp[2]
        dist_xz = math.sqrt(dx * dx + dz * dz)
        self.cam.yaw = math.atan2(dx, dz)
        self.cam.pitch = math.atan2(-dy, dist_xz)
        self.cam.roll = 0.0

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

            # Oblicz kolor wg modelu Phonga
            base_color = hex_to_float(poly.color)
            center = polygon_center(poly)
            lit_rgb = phong_shading(
                poly.normal, center, cam_pos,
                self.light, self.material, base_color
            )
            fill_color = f"#{lit_rgb[0]:02x}{lit_rgb[1]:02x}{lit_rgb[2]:02x}"

            cv.create_polygon(
                flat_pts,
                fill=fill_color,
                outline="",
                width=0,
                stipple="gray50" if self.stipple_on else "",
            )

        # --- 3. Marker pozycji swiatla (zolty krzyzyk) ---
        lp = self.light.position
        lp_cam = mat4_vec(view, [lp[0], lp[1], lp[2], 1.0])
        lp_scr = self._project_point(lp_cam, f, cx, cy, scale)
        if lp_scr:
            lx, ly = lp_scr
            sz = 8
            cv.create_line(lx - sz, ly, lx + sz, ly, fill="#ffff00", width=2)
            cv.create_line(lx, ly - sz, lx, ly + sz, fill="#ffff00", width=2)
            cv.create_text(lx + 12, ly - 8, anchor="nw", fill="#ffff00",
                           font=("Consolas", 8), text="LIGHT")

        # HUD - informacje o kamerze
        c = self.cam
        info = (
            f"Poz: ({c.x:.1f}, {c.y:.1f}, {c.z:.1f})   "
            f"Yaw: {math.degrees(c.yaw):.0f} deg   "
            f"Pitch: {math.degrees(c.pitch):.0f} deg   "
            f"Roll: {math.degrees(c.roll):.0f} deg   "
            f"FOV: {c.fov:.0f} deg"
        )
        stipple_label = "[ON]" if self.stipple_on else "[OFF]"
        cv.create_text(
            10, 10, anchor="nw", fill="white",
            font=("Consolas", 10), text=info,
        )
        cv.create_text(
            10, 28, anchor="nw", fill="#888888",
            font=("Consolas", 9),
            text=f"WASD=ruch  Q/E=gora/dol  "
                 f"Strzalki=obrot  Z/X=przechylenie  "
                 f"+/-=zoom  R=reset  L=POV swiatla  "
                 f"T = stipple {stipple_label}"
        )


if __name__ == "__main__":
    App()
