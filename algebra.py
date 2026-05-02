"""Algebra macierzowa i wektorowa 3D - operacje matematyczne."""
import math


# ======================== Macierze 4x4 ========================

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


# ======================== Wektory 3D ========================

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
