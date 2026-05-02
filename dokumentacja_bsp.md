# Dokumentacja: Eliminacja elementów zasłoniętych algorytmem BSP

## Czym jest BSP?

**BSP (Binary Space Partitioning)** to algorytm podziału przestrzeni 3D na dwie połowy za pomocą płaszczyzn. Buduje się drzewo binarne, w którym każdy węzeł reprezentuje płaszczyznę dzielącą przestrzeń. Dzięki temu można w czasie renderowania ustalić poprawną kolejność rysowania wielokątów (od najdalszych do najbliższych — tzw. **algorytm malarza**), co eliminuje problem zasłaniania: bliższe obiekty po prostu zamalowują dalsze.

---

## Struktura programu — omówienie kodu

### 1. Algebra wektorowa 3D (nowe funkcje pomocnicze)

```python
def vec3_sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
```
Oblicza różnicę dwóch wektorów 3D (a - b). Potrzebne do wyznaczania krawędzi wielokąta.

```python
def vec3_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
```
Iloczyn skalarny — mierzy "jak bardzo" dwa wektory są równoległe. Używany do sprawdzania, po której stronie płaszczyzny leży punkt.

```python
def vec3_cross(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
```
Iloczyn wektorowy — daje wektor prostopadły do dwóch wektorów wejściowych. Używany do obliczenia normalnej ściany (kierunku "na zewnątrz").

```python
def vec3_normalize(v):
    l = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if l < 1e-12:
        return [0, 0, 0]
    return [v[0] / l, v[1] / l, v[2] / l]
```
Normalizacja — skraca/wydłuża wektor do długości 1, zachowując kierunek. Chroni przed dzieleniem przez zero (jeśli wektor jest zerowy).

---

### 2. Rozszerzenie klasy Mesh o ściany (faces)

```python
class Mesh:
    def __init__(self, vertices, edges, color="white", faces=None):
        self.vertices = vertices   # [[x, y, z], ...]
        self.edges = edges         # [(i, j), ...]
        self.faces = faces or []   # [[i, j, k, ...], ...]
        self.color = color
```
Wcześniej `Mesh` przechowywał tylko wierzchołki i krawędzie (wireframe). Teraz dodano pole `faces` — lista ścian, gdzie każda ściana to lista indeksów wierzchołków tworzących wielokąt. Bez ścian nie można stosować BSP, bo algorytm operuje na płaskich wielokątach, nie na krawędziach.

Przykład dla sześcianu:
```python
faces = [
    [0, 2, 3, 1],  # lewa  (-X)
    [4, 5, 7, 6],  # prawa (+X)
    [0, 1, 5, 4],  # dol   (-Y)
    [2, 6, 7, 3],  # gora  (+Y)
    [0, 4, 6, 2],  # tyl   (-Z)
    [1, 3, 7, 5],  # przod (+Z)
]
```
Każda podlista to 4 indeksy wierzchołków tworzących jedną ścianę sześcianu. Kolejność jest ważna — definiuje kierunek normalnej (na zewnątrz bryły).

---

### 3. Klasa Polygon — wielokąt w BSP

```python
class Polygon:
    def __init__(self, vertices, color="white"):
        self.vertices = vertices  # [[x, y, z], ...]
        self.color = color
        self.normal = [0, 0, 0]
        self.d = 0.0
        if len(vertices) >= 3:
            edge1 = vec3_sub(vertices[1], vertices[0])
            edge2 = vec3_sub(vertices[2], vertices[0])
            self.normal = vec3_normalize(vec3_cross(edge1, edge2))
            self.d = -vec3_dot(self.normal, vertices[0])
```

**Co tu się dzieje:**
1. Bierzemy 3 pierwsze wierzchołki wielokąta
2. Obliczamy dwa wektory krawędzi (`edge1`, `edge2`)
3. Iloczyn wektorowy tych krawędzi daje normalną ściany (`normal`)
4. Obliczamy `d` — przesunięcie płaszczyzny od początku układu współrzędnych

Razem `normal` i `d` definiują **równanie płaszczyzny**: $N \cdot P + d = 0$

Każdy punkt w przestrzeni 3D można wstawić w to równanie:
- wynik > 0 → punkt leży **przed** płaszczyzną (strona FRONT)
- wynik < 0 → punkt leży **za** płaszczyzną (strona BACK)
- wynik ≈ 0 → punkt leży **w** płaszczyźnie (COPLANAR)

---

### 4. Klasyfikacja punktu względem płaszczyzny

```python
EPSILON = 1e-5
FRONT = 1
BACK = -1
COPLANAR = 0
SPANNING = 2

def classify_point(normal, d, point):
    dist = vec3_dot(normal, point) + d
    if dist > EPSILON:
        return FRONT
    elif dist < -EPSILON:
        return BACK
    return COPLANAR
```

Oblicza odległość punktu od płaszczyzny (ze znakiem). `EPSILON` to mały margines tolerancji — zapobiega błędom zaokrągleń (punkt "prawie na płaszczyźnie" traktowany jako COPLANAR).

---

### 5. Klasyfikacja wielokąta względem płaszczyzny

```python
def classify_polygon(splitter, poly):
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
```

Sprawdza każdy wierzchołek wielokąta i zlicza, ile jest po stronie przedniej, a ile po tylnej:
- Wszystkie z przodu → cały wielokąt jest FRONT
- Wszystkie z tyłu → cały wielokąt jest BACK
- Mieszanka → wielokąt jest **SPANNING** (przecina płaszczyznę — trzeba go podzielić!)
- Żaden nie jest po żadnej stronie → COPLANAR (leży w tej samej płaszczyźnie)

---

### 6. Podział wielokąta przecinającego płaszczyznę

```python
def split_polygon(splitter_normal, splitter_d, poly):
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
```

**Kluczowa operacja BSP** — gdy wielokąt przecina płaszczyznę podziału, dzielimy go na dwa mniejsze:

1. Iterujemy po krawędziach wielokąta (para kolejnych wierzchołków `vi`, `vj`)
2. Klasyfikujemy oba końce krawędzi
3. Jeśli wierzchołek jest po stronie FRONT — dodajemy go do `front_verts`
4. Jeśli jest po stronie BACK — dodajemy do `back_verts`
5. **Jeśli krawędź przecina płaszczyznę** (jeden koniec FRONT, drugi BACK):
   - Wyznaczamy parametr `t` — gdzie dokładnie krawędź przecina płaszczyznę
   - Obliczamy punkt przecięcia (`intersection`)
   - Dodajemy go do **obu** list (staje się nowym wierzchołkiem obu połówek)

Wynik: dwa nowe wielokąty, każdy w całości po jednej stronie płaszczyzny.

---

### 7. Węzeł drzewa BSP

```python
class BSPNode:
    def __init__(self):
        self.polygon = None     # wielokat definiujacy plaszczyzne podzialu
        self.coplanar = []      # wielokaty lezace w tej samej plaszczyznie
        self.front = None       # poddrzewo - strona przednia
        self.back = None        # poddrzewo - strona tylna
```

Każdy węzeł przechowuje:
- `polygon` — wielokąt, którego płaszczyzna dzieli przestrzeń na dwie połowy
- `coplanar` — wielokąty leżące dokładnie w tej samej płaszczyźnie
- `front` — poddrzewo z wielokątami po stronie przedniej
- `back` — poddrzewo z wielokątami po stronie tylnej

---

### 8. Budowanie drzewa BSP

```python
def build_bsp_tree(polygons):
    if not polygons:
        return None

    node = BSPNode()
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
```

**Algorytm rekurencyjny:**
1. Jeśli lista wielokątów jest pusta → zwróć `None` (liść drzewa)
2. Weź pierwszy wielokąt jako "splitter" — jego płaszczyzna dzieli przestrzeń
3. Dla każdego pozostałego wielokąta:
   - **COPLANAR** → dodaj do tego samego węzła
   - **FRONT** → dodaj do listy "przód"
   - **BACK** → dodaj do listy "tył"
   - **SPANNING** → podziel na dwa i dodaj odpowiednie połówki
4. Rekurencyjnie buduj poddrzewo z listy "przód" i z listy "tył"

Drzewo budujemy **raz** przy starcie programu (scena jest statyczna).

---

### 9. Przechodzenie drzewa BSP (algorytm malarza)

```python
def traverse_bsp(node, camera_pos, result):
    if node is None:
        return

    side = classify_point(node.polygon.normal, node.polygon.d, camera_pos)

    if side == FRONT:
        traverse_bsp(node.back, camera_pos, result)
        result.extend(node.coplanar)
        traverse_bsp(node.front, camera_pos, result)
    else:
        traverse_bsp(node.front, camera_pos, result)
        result.extend(node.coplanar)
        traverse_bsp(node.back, camera_pos, result)
```

**Serce renderowania** — w każdej klatce ustalamy kolejność rysowania:

1. Sprawdzamy, po której stronie płaszczyzny węzła jest kamera (`side`)
2. Jeśli kamera jest po stronie FRONT:
   - Najpierw rysuj to, co za płaszczyzną (BACK) — jest dalej od kamery
   - Potem rysuj wielokąty w tej płaszczyźnie
   - Na końcu rysuj to, co przed płaszczyzną (FRONT) — jest bliżej kamery
3. Jeśli kamera jest po stronie BACK — odwrotna kolejność

**Efekt:** wielokąty trafiają do listy `result` w kolejności od najdalszego do najbliższego. Rysowane w tej kolejności, bliższe zamalowują dalsze — to eliminuje problem zasłaniania.

---

### 10. Konwersja siatek na wielokąty

```python
def meshes_to_polygons(meshes):
    polygons = []
    for mesh in meshes:
        for face in mesh.faces:
            verts = [list(mesh.vertices[i]) for i in face]
            polygons.append(Polygon(verts, mesh.color))
    return polygons
```

Bierze wszystkie siatki z faces i tworzy z nich płaską listę obiektów `Polygon` — gotową do wstawienia w drzewo BSP.

---

### 11. Renderowanie w klasie App

```python
# Budujemy drzewo BSP ze scian (faces) obiektow
solid_meshes = [m for m in self.scene_meshes if m.faces]
self.polygons = meshes_to_polygons(solid_meshes)
self.bsp_tree = build_bsp_tree(self.polygons)

# Siatki bez scian (grid, osie) - rysowane jako wireframe
self.wireframe_meshes = [m for m in self.scene_meshes if not m.faces]
```

Przy inicjalizacji:
- Siatki **z faces** (sześciany, piramidy, ośmiościan) → budujemy z nich drzewo BSP
- Siatki **bez faces** (siatka podłogi, osie XYZ) → rysowane klasycznie jako linie

```python
# W metodzie _render():

# --- 1. Rysuj wireframe (siatka podlogi, osie) ---
for mesh in self.wireframe_meshes:
    # ... standardowe rysowanie linii ...

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
    cv.create_polygon(
        flat_pts,
        fill=self._darken_color(poly.color, 0.5),
        outline=poly.color,
        width=1,
    )
```

Proces renderowania jednej klatki:
1. Pobierz pozycję kamery w świecie
2. Przejdź drzewo BSP → uzyskaj listę wielokątów od najdalszego do najbliższego
3. Dla każdego wielokąta:
   - Przetransformuj wierzchołki macierzą widoku (świat → kamera)
   - Rzutuj na ekran (perspektywa)
   - Rysuj wypełniony wielokąt (`create_polygon`) z ciemniejszym kolorem wewnątrz i jaśniejszym konturem

---

### 12. Przyciemnianie koloru

```python
@staticmethod
def _darken_color(hex_color, factor):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r = int(int(hex_color[0:2], 16) * factor)
        g = int(int(hex_color[2:4], 16) * factor)
        b = int(int(hex_color[4:6], 16) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    return "#000000"
```

Mnoży składowe RGB koloru przez `factor` (0.5 = 50% jasności). Dzięki temu wnętrze ściany jest ciemniejsze od krawędzi, co daje efekt wizualny głębi.

---

## Podsumowanie przepływu algorytmu

```
INICJALIZACJA (raz):
  1. Utwórz obiekty 3D (sześciany, piramidy, ośmiościan) z definicjami ścian
  2. Zamień ściany na obiekty Polygon (z normalnymi i płaszczyznami)
  3. Zbuduj drzewo BSP (rekurencyjny podział przestrzeni)

KAŻDA KLATKA:
  1. Pobierz pozycję kamery
  2. Przejdź drzewo BSP back-to-front → posortowana lista wielokątów
  3. Dla każdego wielokąta (od najdalszego):
     a. Transformuj do układu kamery
     b. Rzutuj perspektywicznie na ekran 2D
     c. Rysuj wypełniony wielokąt (bliższe zamalowują dalsze)
```

---

## Sterowanie

| Klawisz | Działanie |
|---------|-----------|
| W/A/S/D | Ruch przód/lewo/tył/prawo |
| Q/E | Ruch góra/dół |
| Strzałki | Obrót kamery (yaw/pitch) |
| Z/X | Przechylenie (roll) |
| +/- | Zoom (FOV) |
| R | Reset kamery |
