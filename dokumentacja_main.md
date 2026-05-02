# Dokumentacja: Główna aplikacja (plik `main.py`)

## O czym jest ten plik?

`main.py` łączy wszystkie moduły w jedną aplikację. Tworzy okno tkinter, buduje scenę 3D, obsługuje klawiaturę, buduje drzewo BSP i w każdej klatce renderuje scenę z oświetleniem Phonga.

---

## 1. Importy

```python
import tkinter as tk
import math

from algebra import mat4_vec
from modele import make_cube, make_pyramid, make_octahedron, make_grid, make_axes
from bsp import build_bsp_tree, traverse_bsp, meshes_to_polygons
from oswietlenie import PointLight, Material, phong_shading, hex_to_float, polygon_center
from kamera import Camera
```

**Co to robi:** Ściąga potrzebne narzędzia z każdego modułu. `algebra` — mnożenie macierzy razy wektor. `modele` — fabryki brył. `bsp` — drzewo BSP i sortowanie. `oswietlenie` — Phong. `kamera` — klasa kamery.

**Dla debila:** Na początku mówisz Pythonowi "potrzebuję tego, tego i tego z tamtych plików". Każdy plik to osobna szuflada z narzędziami. `main.py` otwiera wszystkie szuflady i bierze co mu potrzebne.

---

## 2. Klasa App — stałe i inicjalizacja

```python
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
```

**Co to robi:** Tworzy okno 900×650 z czarnym płótnem (Canvas). Ustawia prędkość ruchu/obrotu/zoomu. Tworzy kamerę i buduje scenę.

**Dla debila:** Otwiera czarne okno. Ustawia "szybkość chodzenia" i "szybkość kręcenia głową". Tworzy kamerę (twoje oczy w 3D) i ustawia wszystkie obiekty w świecie.

### Światło i materiał

```python
        self.light = PointLight(
            position=[5.0, 8.0, -3.0],
            color=(1.0, 1.0, 0.95),
            intensity=1.0
        )
        self.material = Material(
            ambient=0.15,
            diffuse=0.7,
            specular=0.4,
            shininess=32
        )
```

**Co to robi:** Tworzy lampę punktową na pozycji (5, 8, -3) z ciepło-białym kolorem i materiał z umiarkowanymi parametrami Phonga.

**Dla debila:** Wieszasz lampę wysoko z prawej strony sceny. Ustawiasz "skórę" obiektów — trochę widać w cieniu (0.15), mocno reaguje na światło (0.7), średni połysk (0.4), błysk dość ostry (32).

### Budowa drzewa BSP

```python
        solid_meshes = [m for m in self.scene_meshes if m.faces]
        self.polygons = meshes_to_polygons(solid_meshes)
        self.bsp_tree = build_bsp_tree(self.polygons)

        self.wireframe_meshes = [m for m in self.scene_meshes if not m.faces]
```

**Co to robi:** Dzieli siatki na dwie grupy: te z faces (bryły — trafiają do BSP) i te bez (wireframe — siatka podłogi, osie). Z brył wyciąga wielokąty i buduje drzewo BSP. Robione **raz** przy starcie programu.

**Dla debila:** Bierzesz wszystkie "pełne" obiekty (kostki, piramidy) i robisz z nich drzewo BSP. Siatka podłogi i osie nie mają ścian — rysowane osobno jako linie. Drzewo budujesz raz na starcie i potem korzystasz z niego w każdej klatce.

---

## 3. Budowa sceny

```python
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
```

**Co to robi:** Tworzy scenę z 3 sześcianów (cyan, zielony, fioletowy), 2 piramid (żółta, różowa), 1 ośmiościan (pomarańczowy), siatkę podłogi na y=-1.5 i osie XYZ.

**Dla debila:** Stawiasz obiekty w świecie jak meble w pokoju. Trzy kolorowe kostki, dwie piramidy, jeden "diament", podłoga w kratkę i trzy kolorowe patykowate linie (osie). Każdy obiekt ma swoją pozycję, rozmiar i kolor.

---

## 4. Obsługa klawiatury

```python
        self.keys = set()
        self.root.bind("<KeyPress>",   lambda e: self.keys.add(e.keysym.lower()))
        self.root.bind("<KeyRelease>", lambda e: self.keys.discard(e.keysym.lower()))
```

**Co to robi:** Zbiera aktualnie wciśnięte klawisze do zbioru (set). Przy naciśnięciu dodaje, przy puszczeniu usuwa. Dzięki temu można wciskać kilka klawiszy naraz.

**Dla debila:** Program pamięta jakie klawisze są wciśnięte w danym momencie. Jak trzymasz W i A jednocześnie — oba są w zbiorze i możesz iść do przodu i w lewo jednocześnie.

### Ruch i obroty kamery

```python
    def _handle_input(self):
        c = self.cam
        fwd = c.forward_vec()
        rgt = c.right_vec()
        m = self.MOVE_SPEED

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
```

**Co to robi:** W/S = ruch do przodu/tyłu wzdłuż wektora "forward" kamery. A/D = ruch w lewo/prawo wzdłuż wektora "right". Q/E = ruch w górę/dół (po osi Y świata). Ruch jest w lokalnym układzie kamery — "do przodu" znaczy "tam gdzie kamera patrzy".

**Dla debila:** WASD jak w grze FPS. W = idź tam gdzie patrzysz. S = cofaj się. A = krok w lewo. D = krok w prawo. Q = leć do góry. E = leć w dół. Wszystko relatywne do tego, w którą stronę patrzysz.

```python
        r = self.ROT_SPEED
        if 'left'  in self.keys: c.yaw   -= r
        if 'right' in self.keys: c.yaw   += r
        if 'up'    in self.keys: c.pitch -= r
        if 'down'  in self.keys: c.pitch += r
        if 'z'     in self.keys: c.roll  -= r
        if 'x'     in self.keys: c.roll  += r
```

**Co to robi:** Strzałki lewo/prawo = obrót yaw (jak kręcenie głową). Góra/dół = obrót pitch (patrzenie w górę/dół). Z/X = przechylenie roll (jak przechylanie głowy na bok).

**Dla debila:** Strzałki = kręcisz głową lewo-prawo i góra-dół. Z/X = przechylasz głowę na bok (jak gdybyś kładł ucho na ramię).

```python
        z = self.ZOOM_SPEED
        if 'plus' in self.keys or 'equal' in self.keys or 'kp_add' in self.keys:
            c.fov = max(10, c.fov - z)
        if 'minus' in self.keys or 'kp_subtract' in self.keys:
            c.fov = min(160, c.fov + z)

        if 'r' in self.keys:
            c.reset()
```

**Co to robi:** +/- = zmiana FOV (pole widzenia). Mniejsze FOV = "zoom in". Większe = "zoom out". Zakres 10°–160°. R = reset kamery do pozycji startowej.

**Dla debila:** Plus = przybliż (jak lornetka). Minus = oddal (jak rybie oko). R = wróć na start, jakby ktoś nacisnął restart.

---

## 5. Pętla renderowania

```python
    def _tick(self):
        self._handle_input()
        self._render()
        self.root.after(16, self._tick)
```

**Co to robi:** Co 16 ms (≈60 FPS) obsługuje klawiaturę i rysuje nową klatkę. `after(16, self._tick)` planuje następne wywołanie.

**Dla debila:** 60 razy na sekundę: sprawdź klawiaturę → narysuj obraz → powtórz. Dlatego ruch jest płynny.

### Projekcja 3D → 2D

```python
    def _project_point(self, point_cam, f, cx, cy, scale):
        if point_cam[2] <= 0.1:
            return None
        px = point_cam[0] * f / point_cam[2]
        py = point_cam[1] * f / point_cam[2]
        sx = cx + px * scale
        sy = cy - py * scale
        return (sx, sy)
```

**Co to robi:** Rzutowanie perspektywiczne. Dzieli x i y przez z (głębokość) — obiekty dalej są mniejsze. `f` to współczynnik z FOV. Jeśli punkt jest za kamerą (z ≤ 0.1) — nie rysujemy go. Na końcu przesuwa do środka ekranu i skaluje.

**Dla debila:** Zamienia punkt 3D na piksel na ekranie. Rzeczy dalej od kamery są mniejsze (bo dzielisz przez odległość). Rzeczy za kamerą ignorujesz. Potem przesuwasz wynik na środek okna.

---

## 6. Rysowanie klatki — `_render()`

### 6.1 Wireframe (siatka + osie)

```python
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
```

**Co to robi:** Dla siatek bez ścian (grid, osie): transformuje wierzchołki do układu kamery (`mat4_vec` z macierzą widoku), rzutuje na ekran i rysuje linie. Siatka rysowana **przed** BSP — wielokąty BSP mogą ją zasłonić.

**Dla debila:** Rysuje linie podłogi i kolorowe osie. Każdy punkt z 3D zamieniany na piksel na ekranie. Potem łączy punkty linią. Rysowane jako pierwsze — pełne ściany obiektów namalowane później je zasłonią (tak jak malarz maluje tło a potem obiekty na wierzchu).

### 6.2 BSP — wypełnione ściany z Phongiem

```python
        cam_pos = [self.cam.x, self.cam.y, self.cam.z]
        sorted_polys = []
        traverse_bsp(self.bsp_tree, cam_pos, sorted_polys)

        for poly in sorted_polys:
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

            flat_pts = [coord for pt in screen_pts for coord in pt]

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
            )
```

**Co to robi:**
1. Sortuje wielokąty BSP od dalszego do bliższego (algorytm malarza).
2. Dla każdego wielokąta: transformuje do kamery, rzutuje na ekran.
3. Oblicza kolor Phonga: zamienia hex na float, liczy środek ściany, woła `phong_shading()`.
4. Rysuje wypełniony wielokąt (`create_polygon`) bez obramowania (`outline=""`, `width=0`).

**Dla debila:** 
1. Pytasz drzewo BSP "w jakiej kolejności malować ściany?" — odpowiada: "najpierw dalsze, potem bliższe".
2. Każdą ścianę zamieniasz z 3D na piksele na ekranie.
3. Pytasz oświetlenie Phonga "jaki kolor ma ta ściana?" — odpowiada np. "#2a8888" (ciemny turkus).
4. Malujesz ścianę tym kolorem. Bliższe ściany malują się na wierzchu dalszych.

### 6.3 Marker światła i HUD

```python
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
```

**Co to robi:** Rysuje żółty krzyżyk + napis "LIGHT" w miejscu gdzie jest lampa. Pozycja lampy jest rzutowana na ekran tak jak każdy inny punkt.

**Dla debila:** Na ekranie pojawia się żółty "plus" w miejscu lampy z napisem LIGHT. Dzięki temu widzisz skąd pada światło.

```python
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
```

**Co to robi:** Wyświetla w lewym górnym rogu pozycję kamery, kąty obrotu, FOV i opis sterowania. Tekst rysowany na samym końcu — zawsze na wierzchu.

**Dla debila:** U góry ekranu widać gdzie jesteś i w którą stronę patrzysz. Pod spodem jest ściągawka ze sterowaniem.

---

## 7. Uruchomienie

```python
if __name__ == "__main__":
    App()
```

**Co to robi:** Jeśli plik uruchamiany bezpośrednio (nie importowany), tworzy obiekt App — co uruchamia okno i pętlę główną.

**Dla debila:** "Jak klikniesz ten plik — odpal program". Tylko to.

---

## Pipeline renderowania — podsumowanie kolejności

1. `cv.delete("all")` — wyczyść ekran
2. **Wireframe** — rysuj siatkę podłogi i osie (linie)
3. **BSP traverse** — posortuj ściany brył od dalszej do bliższej
4. **Phong + create_polygon** — dla każdej ściany policz kolor oświetlenia i narysuj wypełniony wielokąt
5. **Marker światła** — żółty krzyżyk w pozycji lampy
6. **HUD** — pozycja kamery i sterowanie
