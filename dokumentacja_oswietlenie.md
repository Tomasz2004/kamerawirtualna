# Dokumentacja: Oświetlenie Phonga (plik `oswietlenie.py`)

## Czym jest model Phonga?

**Model Phonga** to sposób obliczania koloru powierzchni w zależności od kąta padania światła, pozycji kamery i właściwości materiału. Łączy trzy składniki: ambient (tło), diffuse (rozproszenie) i specular (odbłysk). Daje realistyczny efekt cieniowania bez śledzenia promieni.

---

## 1. Źródło światła punktowego

```python
class PointLight:
    def __init__(self, position, color=(1.0, 1.0, 1.0), intensity=1.0):
        self.position = position
        self.color = color
        self.intensity = intensity
```

**Co to robi:** Definiuje punkt w przestrzeni, z którego "bije" światło. `position` to współrzędne [x, y, z] lampy. `color` to barwa światła (domyślnie biała). `intensity` to mnożnik jasności.

**Dla debila:** To żarówka wisząca w powietrzu. Mówisz jej: "wisisz tu, świecisz takim kolorem, taką mocą". Potem kod patrzy, jak daleko jest od niej każda ściana i pod jakim kątem pada światło.

W `main.py` światło jest ustawione tak:
```python
self.light = PointLight(
    position=[5.0, 8.0, -3.0],
    color=(1.0, 1.0, 0.95),
    intensity=1.0
)
```
Lampa wisi na pozycji (5, 8, -3) — wysoko i trochę z boku. Kolor lekko ciepły (0.95 w niebieskim zamiast 1.0).

---

## 2. Materiał powierzchni

```python
class Material:
    def __init__(self, ambient=0.15, diffuse=0.7, specular=0.5, shininess=32):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
```

**Co to robi:** Opisuje, jak powierzchnia reaguje na światło. `ambient` — ile światła widać nawet bez bezpośredniego oświetlenia (tło). `diffuse` — ile światła się rozprasza (matowe odbicie). `specular` — siła błysku lustrzanego. `shininess` — ostrość błysku (większa = mniejszy, ostrzejszy punkt świetlny).

**Dla debila:** To "skóra" obiektu. `ambient` = minimum jasności żeby coś w ogóle było widać w cieniu. `diffuse` = jak bardzo powierzchnia się rozjaśnia kiedy światło na nią padnie. `specular` = czy jest taki biały punkcik (jak na szklance). `shininess` = ten punkcik jest mały i ostry (dużo) czy duży i rozmyty (mało).

W `main.py` materiał jest ustawiony tak:
```python
self.material = Material(
    ambient=0.15,
    diffuse=0.7,
    specular=0.4,
    shininess=32
)
```
15% jasności nawet w cieniu, mocne rozproszenie (0.7), średni odbłysk (0.4), umiarkowana ostrość (32).

---

## 3. Obliczanie koloru — `phong_shading()`

```python
def phong_shading(normal, face_center, camera_pos, light, material, base_color):
    # Kierunek do swiatla
    L = vec3_normalize(vec3_sub(light.position, face_center))
    # Kierunek do kamery (obserwatora)
    V = vec3_normalize(vec3_sub(camera_pos, face_center))
```

**Co to robi:** Oblicza dwa podstawowe wektory: `L` — kierunek od środka ściany do lampy, `V` — kierunek od środka ściany do kamery. Oba znormalizowane (długość = 1).

**Dla debila:** Stoisz na ścianie i rozglądasz się. Pokazujesz jedną ręką na lampę (`L`) i drugą na kamerę (`V`). Potem obliczasz kąty żeby wiedzieć, ile światła dociera i ile odbija się w twoim kierunku.

### 3.1 Komponent ambient (tło)

```python
    ambient_r = material.ambient * base_color[0]
    ambient_g = material.ambient * base_color[1]
    ambient_b = material.ambient * base_color[2]
```

**Co to robi:** Stałe minimum jasności — niezależne od pozycji lampy ani kamery. Po prostu `base_color × ambient_factor`. Zapewnia, że nawet ściany odwrócone od światła nie są 100% czarne.

**Dla debila:** Nawet w nocy coś widzisz, bo jest światło "z otoczenia". Ten kod mówi: "nawet jak lampa nie oświetla ściany, weź 15% koloru bazowego żeby nie była zupełnie czarna".

### 3.2 Komponent diffuse (Lambert)

```python
    NdotL = max(0.0, vec3_dot(normal, L))
    diffuse_r = material.diffuse * NdotL * base_color[0] * light.color[0] * light.intensity
    diffuse_g = material.diffuse * NdotL * base_color[1] * light.color[1] * light.intensity
    diffuse_b = material.diffuse * NdotL * base_color[2] * light.color[2] * light.intensity
```

**Co to robi:** `NdotL` = cosinus kąta między normalną ściany a kierunkiem do lampy. Ściana zwrócona prosto do lampy → `NdotL ≈ 1.0` (jasna). Ściana odwrócona → `NdotL = 0.0` (ciemna). Wynik mnożony przez kolor ściany, kolor lampy i intensywność.

**Dla debila:** Iloczyn skalarny `N·L` to "jak bardzo ściana patrzy na lampę". Wartość 1.0 = patrzy prosto. 0 = jest bokiem/tyłem. Jak ściana patrzy na lampę — jest jasna. Jak jest odwrócona — ciemna. To prawo Lamberta — nic skomplikowanego.

### 3.3 Komponent specular (odbłysk lustrzany)

```python
    NdotL2 = vec3_dot(normal, L)
    R = [
        2.0 * NdotL2 * normal[0] - L[0],
        2.0 * NdotL2 * normal[1] - L[1],
        2.0 * NdotL2 * normal[2] - L[2],
    ]
    R = vec3_normalize(R)
    RdotV = max(0.0, vec3_dot(R, V))
    spec_factor = pow(RdotV, material.shininess) if NdotL > 0 else 0.0
    specular_r = material.specular * spec_factor * light.color[0] * light.intensity
    specular_g = material.specular * spec_factor * light.color[1] * light.intensity
    specular_b = material.specular * spec_factor * light.color[2] * light.intensity
```

**Co to robi:** Oblicza wektor odbicia `R = 2(N·L)N - L` — kierunek, w którym światło "odbiłoby się" od ściany jak od lustra. Potem sprawdza, jak blisko tego kierunku jest kamera (`RdotV`). Im bliżej — tym jaśniejszy odbłysk. Podnosi do potęgi `shininess` — to sprawia, że wartości bliskie 1.0 zostają jasne, a reszta szybko spada do zera (efekt ostrego błysku). Spec jest biały (nie zależy od koloru bazowego ściany).

**Dla debila:** Wyobraź sobie lusterko na ścianie. Promień światła odbija się i leci dalej. Jeśli akurat trafia w twoje oko (kamerę) — widzisz jasny punkcik. `shininess` to ile "skupiony" jest ten odbłysk: dużo = mały punkcik, mało = rozmyty jasny plam.

### 3.4 Sumowanie komponentów

```python
    r = min(1.0, ambient_r + diffuse_r + specular_r)
    g = min(1.0, ambient_g + diffuse_g + specular_g)
    b = min(1.0, ambient_b + diffuse_b + specular_b)

    return (int(r * 255), int(g * 255), int(b * 255))
```

**Co to robi:** Dodaje trzy składniki (ambient + diffuse + specular) i ogranicza do 1.0 (żeby nie przekroczyć zakresu). Potem mnoży przez 255, żeby dostać wartości RGB dla tkinter.

**Dla debila:** Mieszasz trzy warstwy farby — tło + główne oświetlenie + błysk — i upewniasz się, że nic nie jest "jaśniejsze niż białe". Potem zamieniasz 0.0–1.0 na 0–255 bo tak działa kolor na ekranie.

---

## 4. Konwersja kolorów hex → float

```python
def hex_to_float(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        return (
            int(hex_color[0:2], 16) / 255.0,
            int(hex_color[2:4], 16) / 255.0,
            int(hex_color[4:6], 16) / 255.0,
        )
    return (1.0, 1.0, 1.0)
```

**Co to robi:** Zamienia kolor w formacie `"#00dddd"` na trójkę (r, g, b) w zakresie 0..1. Potrzebne, bo Phong liczy na floatach, a kolory w modelu podane są jako hex.

**Dla debila:** Kolor jak `"#ff0000"` (czerwony) zamienia na `(1.0, 0.0, 0.0)`. Bo w kodzie kolory to teksty z hashtagiem, a matematyka potrzebuje liczb.

---

## 5. Środek wielokąta

```python
def polygon_center(poly):
    n = len(poly.vertices)
    cx = sum(v[0] for v in poly.vertices) / n
    cy = sum(v[1] for v in poly.vertices) / n
    cz = sum(v[2] for v in poly.vertices) / n
    return [cx, cy, cz]
```

**Co to robi:** Liczy centroid (środek geometryczny) wielokąta — średnia arytmetyczna współrzędnych wszystkich wierzchołków. Używany jako punkt, od którego mierzymy odległość do lampy i kamery przy obliczaniu oświetlenia.

**Dla debila:** Zaznaczasz wszystkie rogi ściany na mapie i stawiasz palec pośrodku. To jest "środek ściany" — od tego punktu mierzymy, jak daleko jest lampa i kamera.

---

## 6. Marker pozycji światła w `main.py`

W głównym pliku lampa jest wizualizowana jako żółty krzyżyk:

```python
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
```

**Co to robi:** Transformuje pozycję lampy do układu kamery, rzutuje na ekran i rysuje żółty krzyżyk + napis "LIGHT". Dzięki temu widać, gdzie jest lampa, co ułatwia debugowanie oświetlenia.

**Dla debila:** Na ekranie rysujemy żółty "plus" w miejscu gdzie wisi lampa i piszemy "LIGHT" obok. Dzięki temu jak poruszasz kamerą, widzisz gdzie jest źródło światła.
