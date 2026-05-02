"""Oswietlenie Phonga - punktowe zrodlo swiatla + material."""
from algebra import vec3_sub, vec3_dot, vec3_normalize


class PointLight:
    """Punktowe zrodlo swiatla."""
    def __init__(self, position, color=(1.0, 1.0, 1.0), intensity=1.0):
        self.position = position    # [x, y, z] w ukladzie swiata
        self.color = color          # (r, g, b) skladowe swiatla 0..1
        self.intensity = intensity  # mnoznik jasnosci


class Material:
    """Material powierzchni - wspolczynniki modelu Phonga."""
    def __init__(self, ambient=0.15, diffuse=0.7, specular=0.5, shininess=32):
        self.ambient = ambient      # wspolczynnik swiatla otoczenia
        self.diffuse = diffuse      # wspolczynnik rozproszenia (Lamberta)
        self.specular = specular    # wspolczynnik odbicia lustrzanego
        self.shininess = shininess  # wykladnik polysku (im wiecej, tym ostrzejszy blask)


def phong_shading(normal, face_center, camera_pos, light, material, base_color):
    """Oblicz kolor sciany wg modelu Phonga.

    Parametry:
        normal      - normalna powierzchni (znormalizowana)
        face_center - srodek sciany [x,y,z]
        camera_pos  - pozycja kamery [x,y,z]
        light       - obiekt PointLight
        material    - obiekt Material
        base_color  - bazowy kolor sciany (r,g,b) 0..1

    Zwraca: (r, g, b) w zakresie 0..255
    """
    # Kierunek do swiatla
    L = vec3_normalize(vec3_sub(light.position, face_center))
    # Kierunek do kamery (obserwatora)
    V = vec3_normalize(vec3_sub(camera_pos, face_center))

    # --- Komponent ambient (swiatlo otoczenia) ---
    ambient_r = material.ambient * base_color[0]
    ambient_g = material.ambient * base_color[1]
    ambient_b = material.ambient * base_color[2]

    # --- Komponent diffuse (rozproszenie Lamberta) ---
    NdotL = max(0.0, vec3_dot(normal, L))
    diffuse_r = material.diffuse * NdotL * base_color[0] * light.color[0] * light.intensity
    diffuse_g = material.diffuse * NdotL * base_color[1] * light.color[1] * light.intensity
    diffuse_b = material.diffuse * NdotL * base_color[2] * light.color[2] * light.intensity

    # --- Komponent specular (odbicie lustrzane) ---
    # Wektor odbicia: R = 2*(N*L)*N - L
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

    # Suma komponentow
    r = min(1.0, ambient_r + diffuse_r + specular_r)
    g = min(1.0, ambient_g + diffuse_g + specular_g)
    b = min(1.0, ambient_b + diffuse_b + specular_b)

    return (int(r * 255), int(g * 255), int(b * 255))


def hex_to_float(hex_color):
    """Konwertuj kolor hex na (r, g, b) w zakresie 0..1."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        return (
            int(hex_color[0:2], 16) / 255.0,
            int(hex_color[2:4], 16) / 255.0,
            int(hex_color[4:6], 16) / 255.0,
        )
    return (1.0, 1.0, 1.0)


def polygon_center(poly):
    """Oblicz srodek (centroid) wielokata."""
    n = len(poly.vertices)
    cx = sum(v[0] for v in poly.vertices) / n
    cy = sum(v[1] for v in poly.vertices) / n
    cz = sum(v[2] for v in poly.vertices) / n
    return [cx, cy, cz]
