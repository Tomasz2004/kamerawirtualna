# Dokumentacja: Modele 3D (plik `modele.py`)

## O czym jest ten plik?

`modele.py` zawiera definicje wszystkich brył 3D w scenie — sześcian, piramida, ośmiościan, siatka podłogi i osie współrzędnych. Każda bryła to obiekt `Mesh` z listą wierzchołków, krawędzi i ścian (faces).

---

## 1. Klasa Mesh

```python
class Mesh:
    def __init__(self, vertices, edges, color="white", faces=None):
        self.vertices = vertices   # [[x, y, z], ...]
        self.edges = edges         # [(i, j), ...]
        self.faces = faces or []   # [[i, j, k, ...], ...] - indeksy wierzcholkow
        self.color = color
```

**Co to robi:** Uniwersalny kontener na bryłę 3D. `vertices` = lista punktów [x,y,z]. `edges` = lista par indeksów (krawędzie do rysowania wireframe). `faces` = lista ścian (każda to lista indeksów wierzchołków w kolejności przeciwnej do zegara patrząc z zewnątrz). `color` = domyślny kolor.

**Dla debila:** Mesh to "pudełko z instrukcją". W środku jest spis rogów (vertices), spis krawędzi łączących rogi (edges) i spis ścian — który róg z którym łączy się w ściankę (faces). Jak budujesz z klocków LEGO — to jest instrukcja budowy jednego klocka.

---

## 2. Sześcian — `make_cube()`

```python
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
```

**Co to robi:** Generuje 8 wierzchołków sześcianu wokół punktu (cx, cy, cz) z podanym rozmiarem. Używa list comprehension z trzema pętlami (-1, 1) — daje wszystkie kombinacje +/- na osiach. Krawędzie (12 sztuk) łączą sąsiednie wierzchołki.

**Dla debila:** Wyobraź sobie kostkę wycentrowaną w punkcie (cx, cy, cz). Ma 8 rogów — każdy to inna kombinacja "lewo/prawo", "góra/dół", "przód/tył". Komentarz w kodzie mówi który numer to który róg, np. 0 = (-,-,-) czyli lewy-dolny-tylny.

### Ściany sześcianu — kolejność wierzchołków

```python
    faces = [
        [1, 3, 2, 0],  # lewa  (-X)
        [6, 7, 5, 4],  # prawa (+X)
        [4, 5, 1, 0],  # dol   (-Y)
        [3, 7, 6, 2],  # gora  (+Y)
        [2, 6, 4, 0],  # tyl   (-Z)
        [5, 7, 3, 1],  # przod (+Z)
    ]
    return Mesh(v, e, color, faces)
```

**Co to robi:** Definiuje 6 ścian sześcianu. Kolejność wierzchołków w każdej ścianie jest taka, że patrząc na nią z zewnątrz, wierzchołki idą **przeciwnie do wskazówek zegara** (CCW). Dzięki temu iloczyn wektorowy (cross product) pierwszych dwóch krawędzi daje normalną skierowaną **na zewnątrz** bryły.

**Dla debila:** Każda ścianka ma 4 rogi podane w takiej kolejności, żeby normalna (strzałka "w którą stronę patrzy ściana") wychodziła NA ZEWNĄTRZ kostki. Gdyby kolejność była odwrócona, normalna wskazywałaby do środka i oświetlenie by nie działało — ściany byłyby ciemne od złej strony.

---

## 3. Piramida — `make_pyramid()`

```python
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
```

**Co to robi:** 5 wierzchołków — 4 rogi kwadratu na dole (y = cy) + 1 czubek na górze (y = cy + height). 8 krawędzi — 4 na dole + 4 do czubka. 5 ścian — kwadratowa podstawa (normalna w dół) + 4 trójkątne boki. Kolejność wierzchołków w ścianach bocznych daje normalne wychodzące na zewnątrz.

**Dla debila:** Piramida = kwadrat na dole + 4 trójkąty prowadzące do czubka. Wierzchołki 0-3 to rogi kwadratu, 4 to czubek. Ściany boczne to trójkąty typu [1, 0, 4] — "weź dwa sąsiednie rogi dołu i czubek".

---

## 4. Ośmiościan — `make_octahedron()`

```python
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
```

**Co to robi:** 6 wierzchołków — po jednym na końcu każdej osi (±X, ±Y, ±Z). 12 krawędzi łączących sąsiednie wierzchołki. 8 trójkątnych ścian — po 4 na górnej i dolnej połówce. To "diament" — dwa czworościany złączone podstawami.

**Dla debila:** Ośmiościan = "diament" albo "dwa daszki klejone brzegami". 6 rogów to punkty na końcach osi (prawo, lewo, góra, dół, przód, tył). Każda ścianka to trójkąt łączący trzy sąsiednie rogi.

---

## 5. Siatka podłogi — `make_grid()`

```python
def make_grid(y, extent, step, color="#444444"):
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
```

**Co to robi:** Generuje linie wzdłuż osi X i Z na stałej wysokości `y`. Dla każdego kroku rysuje jedną linię wzdłuż X i jedną wzdłuż Z. Brak faces — to czysta siatka wireframe.

**Dla debila:** Rysuje kratkę na podłodze. Linie idą w prawo/lewo i przód/tył. Nie ma żadnych ścian — tylko linie. Służy jako "podłoga" żeby widzieć gdzie jest ziemia.

---

## 6. Osie współrzędnych — `make_axes()`

```python
def make_axes(length=15):
    return [
        Mesh([[0, 0, 0], [length, 0, 0]], [(0, 1)], "#ff4444"),
        Mesh([[0, 0, 0], [0, length, 0]], [(0, 1)], "#44ff44"),
        Mesh([[0, 0, 0], [0, 0, length]], [(0, 1)], "#4444ff"),
    ]
```

**Co to robi:** Tworzy 3 oddzielne siatki — po jednej linii na każdą oś: X (czerwona), Y (zielona), Z (niebieska). Każda to dwa punkty + jedna krawędź. Brak faces.

**Dla debila:** Trzy kolorowe patykowate linie wychodzące z punktu (0,0,0): czerwona w prawo (X), zielona do góry (Y), niebieska do przodu (Z). Pomagają zorientować się, gdzie jest "przód" i "góra" w scenie.
