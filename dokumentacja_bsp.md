# Dokumentacja: Algorytm BSP (plik `bsp.py`)

## Czym jest BSP?

**BSP (Binary Space Partitioning)** to algorytm podziału przestrzeni 3D na dwie połowy za pomocą płaszczyzn. Buduje drzewo binarne — każdy węzeł to płaszczyzna dzieląca przestrzeń. Dzięki temu w każdej klatce można ustalić kolejność rysowania wielokątów od najdalszego do najbliższego (algorytm malarza), co eliminuje zasłanianie.

---

## Struktura plików projektu

| Plik | Zawartość |
|------|-----------|
| `algebra.py` | Operacje na macierzach 4×4 i wektorach 3D |
| `modele.py` | Definicje brył (sześcian, piramida, ośmiościan, siatka, osie) |
| `bsp.py` | Algorytm BSP — budowa drzewa i przechodzenie back-to-front |
| `oswietlenie.py` | Model oświetlenia Phonga |
| `kamera.py` | Klasa kamery (pozycja, orientacja, macierz widoku) |
| `main.py` | Główna aplikacja — okno, sterowanie, renderowanie |

---

## 1. Stałe i flagi klasyfikacji

```python
EPSILON = 1e-5

FRONT = 1
BACK = -1
COPLANAR = 0
SPANNING = 2
```

**Co to robi:** Definiuje etykiety stron płaszczyzny. Każdy punkt/wielokąt może być z przodu (FRONT), z tyłu (BACK), w samej płaszczyźnie (COPLANAR) lub po obu stronach naraz (SPANNING). EPSILON to margines błędu — punkt bliżej niż 0.00001 od płaszczyzny traktujemy jako "na niej".

**Dla debila:** Płaszczyzna dzieli świat na dwie połowy. Te 4 stałe to po prostu nazwy: "z przodu", "z tyłu", "dokładnie na", "jedna noga tu druga tam". EPSILON zapobiega sytuacji, że komputer nie wie po której stronie jest punkt bo jest prawie idealnie na granicy.

---

## 2. Klasa Polygon — wielokąt z normalną

```python
class Polygon:
    def __init__(self, vertices, color="white"):
        self.vertices = vertices
        self.color = color
        self.normal = [0, 0, 0]
        self.d = 0.0
        if len(vertices) >= 3:
            edge1 = vec3_sub(vertices[1], vertices[0])
            edge2 = vec3_sub(vertices[2], vertices[0])
            self.normal = vec3_normalize(vec3_cross(edge1, edge2))
            self.d = -vec3_dot(self.normal, vertices[0])
```

**Co to robi:** Tworzy wielokąt 3D i od razu wylicza jego płaszczyznę. `edge1` i `edge2` to dwa boki wielokąta wychodzące z pierwszego wierzchołka. Iloczyn wektorowy (`vec3_cross`) daje normalną — wektor prostopadły do ściany. Potem `d` dopełnia równanie płaszczyzny: `N·P + d = 0`. Każdy punkt P podstawiony do tego wzoru powie nam, po której stronie ściany leży.

**Dla debila:** Wyobraź sobie kartkę papieru wiszącą w powietrzu. Ten kod oblicza, w którą stronę "patrzy" kartka (to normalna). Potem każdy punkt w przestrzeni może zapytać: "jestem przed kartką czy za nią?" — i dostanie odpowiedź.

---

## 3. Klasyfikacja punktu

```python
def classify_point(normal, d, point):
    dist = vec3_dot(normal, point) + d
    if dist > EPSILON:
        return FRONT
    elif dist < -EPSILON:
        return BACK
    return COPLANAR
```

**Co to robi:** Podstawia punkt do równania płaszczyzny. Wynik dodatni = punkt jest z przodu (po stronie normalnej). Ujemny = z tyłu. Bliski zeru = leży w płaszczyźnie.

**Dla debila:** Masz ścianę. Wskazujesz na punkt palcem i pytasz: "jest przede mną, za mną, czy dokładnie obok mnie?". Wartość `dist` to ta odpowiedź — liczba dodatnia = przede mną, ujemna = za mną.

---

## 4. Klasyfikacja wielokąta

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

**Co to robi:** Sprawdza każdy róg wielokąta — po której stronie płaszczyzny leży. Jeśli wszystkie z przodu → FRONT. Wszystkie z tyłu → BACK. Mieszanka → SPANNING (przecina płaszczyznę, trzeba ciąć). Żaden nie jest wyraźnie po żadnej stronie → COPLANAR.

**Dla debila:** Masz trójkąt i nóż (płaszczyznę). Patrzysz na każdy róg trójkąta: "ten jest nad nożem, ten pod nożem, ten też pod". Jeśli rogi są po obu stronach — trójkąt leży na nożu i trzeba go przeciąć na pół.

---

## 5. Podział wielokąta (split)

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

    front_poly = None
    back_poly = None
    if len(front_verts) >= 3:
        front_poly = Polygon(front_verts, poly.color)
        front_poly.normal = list(poly.normal)
        front_poly.d = poly.d
    if len(back_verts) >= 3:
        back_poly = Polygon(back_verts, poly.color)
        back_poly.normal = list(poly.normal)
        back_poly.d = poly.d
    return front_poly, back_poly
```

**Co to robi:** Iteruje po krawędziach wielokąta. Każdy wierzchołek trafia do listy "przód" lub "tył" (albo obu, jeśli COPLANAR). Gdy krawędź przechodzi z jednej strony na drugą — oblicza punkt przecięcia z płaszczyzną (`t` = parametr interpolacji 0..1, `intersection` = punkt na krawędzi) i dodaje go do obu list. Na końcu tworzy dwa nowe wielokąty. **Ważne:** normalna jest kopiowana z oryginału (`front_poly.normal = list(poly.normal)`) — bo nowe wierzchołki mogłyby dać odwróconą normalną.

**Dla debila:** Masz kartkę papieru (wielokąt) i nożyczki (płaszczyznę). Jedziesz nożyczkami wzdłuż płaszczyzny i w miejscu gdzie tną krawędź kartki — stawiasz nowy punkt. Dostajesz dwa kawałki. Oba "pamiętają" z której strony jest ich przód — nie mylą się, bo kopiujemy tę informację z oryginału.

---

## 6. Węzeł drzewa BSP

```python
class BSPNode:
    def __init__(self):
        self.polygon = None
        self.coplanar = []
        self.front = None
        self.back = None
```

**Co to robi:** Jeden węzeł drzewa. `polygon` = wielokąt definiujący płaszczyznę podziału. `coplanar` = wielokąty leżące w tej samej płaszczyźnie. `front` i `back` = poddrzewa (kolejne węzły) dla każdej strony.

**Dla debila:** Pudełko z etykietą. Na etykiecie jest ściana, która dzieli świat na dwie połowy. W lewej szufladce — wszystko co jest z przodu tej ściany. W prawej — z tyłu. W środkowym przegródce — to co leży dokładnie na tej ścianie.

---

## 7. Budowanie drzewa BSP

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

**Co to robi:** Bierze pierwszy wielokąt jako "nóż" (splitter). Każdy inny wielokąt klasyfikuje — jest z przodu, z tyłu, w tej samej płaszczyźnie, czy go przecina. Przecinające dzieli na pół. Potem rekurencyjnie robi to samo dla listy "przód" i "tył". Drzewo budowane jest **raz** — scena się nie zmienia.

**Dla debila:** Masz stos kartek (wielokątów). Bierzesz pierwszą z góry i mówisz: "ta kartka to moja granica". Wszystkie inne kartki sortujesz: "ta jest przede mną, ta za mną, a tę muszę przeciąć". Potem z kupki "przede mną" znowu bierzesz pierwszą i powtarzasz. I tak do końca. Na koniec masz drzewo, które mówi "co jest przed czym".

---

## 8. Przechodzenie drzewa (renderowanie)

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

**Co to robi:** Sprawdza, po której stronie płaszczyzny jest kamera. Jeśli kamera jest z FRONT — najpierw dodaje do listy to co jest BACK (dalsze), potem COPLANAR, potem FRONT (bliższe). Efekt: lista `result` jest posortowana od najdalszego do najbliższego. Rysowanie w tej kolejności = bliższe zamalowują dalsze.

**Dla debila:** Jesteś w pokoju podzielonym ścianą. Stoisz po lewej stronie. Chcesz malować obrazek całego pokoju. Najpierw malujesz to, co jest po DRUGIEJ stronie ściany (bo jest dalej). Potem samą ścianę. Potem to co jest po TWOJEJ stronie (bo jest bliżej). Bliższe rzeczy zamalowują dalsze — jak malarz malujący tło przed pierwszym planem.

---

## 9. Konwersja siatek na wielokąty

```python
def meshes_to_polygons(meshes):
    polygons = []
    for mesh in meshes:
        for face in mesh.faces:
            verts = [list(mesh.vertices[i]) for i in face]
            polygons.append(Polygon(verts, mesh.color))
    return polygons
```

**Co to robi:** Bierze wszystkie siatki z listą ścian (faces) i wyciąga z nich wielokąty Polygon. Dla każdej ściany kopiuje współrzędne wierzchołków i tworzy obiekt Polygon z obliczoną normalną.

**Dla debila:** Masz pudełko (Mesh) z ponumerowanymi rogami i spisem ścian ("ściana 1 to rogi 0, 2, 3, 1"). Ta funkcja bierze ten spis i tworzy osobne karteczki (Polygon) z prawdziwymi współrzędnymi — gotowe do wrzucenia w drzewo BSP.
