"""Kamera wirtualna - pozycja, orientacja, macierz widoku."""
import math
from algebra import mat4_translation, mat4_mul, mat4_rot_x, mat4_rot_y, mat4_rot_z


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
