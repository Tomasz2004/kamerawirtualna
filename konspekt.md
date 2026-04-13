# Kamera wirtualna – konspekt

## Cel projektu

Implementacja interaktywnej kamery wirtualnej operującej na scenie złożonej z wielościanów (sześciany, ostrosłupy, ośmiościany) wyświetlanych w trybie krawędziowym (wireframe). Scena jest definiowana jednokrotnie w układzie świata, a następnie transformowana do układu kamery przy każdej klatce renderingu.

## Podejście

Scena składa się z wielościanów opisanych jako zbiory wierzchołków i krawędzi (model krawędziowy). Kamera posiada pozycję (x, y, z), orientację wyrażoną kątami Eulera (yaw, pitch, roll) oraz pole widzenia (FOV) pełniące jednocześnie rolę zoomu.

Sterowanie odbywa się w **lokalnym układzie kamery** – przesunięcie kamery w lewo powoduje, że cała scena przesuwa się w prawo na ekranie; analogiczna zasada obowiązuje dla obrotów. Użytkownik nie operuje sceną, lecz wyłącznie kamerą: jej położeniem i zoomem.

W każdej klatce budowana jest **macierz widoku 4×4** jako złożenie: translacji o wektor przeciwny do pozycji kamery, a następnie odwrotności macierzy rotacji (Ry · Rx · Rz). Każdy wierzchołek sceny jest mnożony przez tę macierz, przekształcając go do układu kamery. Następnie wykonywany jest **rzut perspektywiczny** na płaszczyznę ekranu – współrzędne dzielone są przez głębokość (z), ze skalowaniem wynikającym z ogniskowej obliczonej na podstawie FOV. Zmniejszenie pola widzenia odpowiada przybliżeniu (zoom in), zwiększenie – oddaleniu (zoom out).

Krawędzie, których choć jeden koniec leży za kamerą (z ≤ 0), są po prostu pomijane – **nie stosujemy przycinania** (clipping). Jeżeli kamera wejdzie do wnętrza wielościanu, obraz może się „rozjechać" – jest to zachowanie akceptowalne; wystarczy wycofać kamerę z obiektu.

Na scenie umieszczono kilka wielościanów o różnych kształtach i rozmiarach, siatkę podłogi oraz osie układu współrzędnych (RGB → XYZ).

## Język i technologia

Program napisany w Pythonie z użyciem wyłącznie biblioteki standardowej (`tkinter` do wyświetlania); cała algebra macierzowa (mnożenie macierzy 4×4, transformacje, rzutowanie) zaimplementowana od podstaw, bez bibliotek zewnętrznych.
