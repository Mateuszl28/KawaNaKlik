"""Wireframe'y (lo-fi) czterech widoków sklepu KawaNaKlik jako SVG.

Szare bloki = treść generowana automatycznie (WordPress / WooCommerce).
Pomarańczowa przerywana ramka + etykieta ACF = element edytowany przez klienta
(pola ACF na zajęciach 2).

Uruchomienie: python wireframes.py  (tworzy *.svg obok skryptu)
"""

from pathlib import Path
from xml.sax.saxutils import escape

W = 1000
OUT = Path(__file__).resolve().parent


class Svg:
    def __init__(self, h, title):
        self.h, self.parts = h, []
        self.rect(0, 0, W, h, fill="#ffffff", stroke="#999", sw=1.5)
        self.text(W - 12, h - 10, title, size=11, anchor="end", fill="#999")

    def rect(self, x, y, w, h, fill="#eeeeee", stroke="#bdbdbd", sw=1, rx=4, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, size=13, weight="normal", anchor="start", fill="#444"):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
                          f'text-anchor="{anchor}" fill="{fill}">{escape(s)}</text>')

    def lines(self, x, y, w, n, gap=14, last=0.6):
        for i in range(n):
            ww = w * (last if i == n - 1 else 1)
            self.rect(x, y + i * gap, ww, 6, fill="#d6d6d6", stroke="none", rx=3)

    def img(self, x, y, w, h, label="obraz"):
        self.rect(x, y, w, h, fill="#e3e3e3")
        self.parts.append(f'<path d="M{x},{y} L{x + w},{y + h} M{x + w},{y} L{x},{y + h}" stroke="#c4c4c4"/>')
        self.text(x + w / 2, y + h / 2 + 4, label, size=11, anchor="middle", fill="#888")

    def button(self, x, y, w, h, label, dark=True):
        self.rect(x, y, w, h, fill="#555" if dark else "#fff", stroke="#555", rx=6)
        self.text(x + w / 2, y + h / 2 + 5, label, size=12, anchor="middle", fill="#fff" if dark else "#333",
                  weight="600")

    def acf(self, x, y, w, h, label):
        self.rect(x - 4, y - 4, w + 8, h + 8, fill="none", stroke="#e07b16", sw=2, dash="6 4", rx=6)
        tw = 8 + len(label) * 6.3
        self.rect(x + w - tw - 2, y - 13, tw + 6, 17, fill="#e07b16", stroke="none", rx=8)
        self.text(x + w - tw / 2 + 1, y, label, size=10.5, anchor="middle", fill="#fff", weight="700")

    def header(self, active=""):
        self.rect(0, 0, W, 64, fill="#f2f2f2", stroke="#bdbdbd", rx=0)
        self.text(30, 40, "KawaNaKlik", size=20, weight="700", fill="#333")
        x = 560
        for item in ("Start", "Sklep", "Blog", "O nas"):
            self.text(x, 38, item, size=13, weight="700" if item == active else "normal", fill="#333")
            x += 70
        self.rect(860, 22, 22, 20, fill="#fff", stroke="#777")
        self.text(890, 37, "Koszyk (2)", size=12, fill="#333")

    def footer(self, y):
        self.rect(0, y, W, self.h - y, fill="#e6e6e6", stroke="#bdbdbd", rx=0)
        self.text(30, y + 30, "Stopka: widgety (o sklepie, najnowsze wpisy), menu w stopce, ©", size=12, fill="#666")
        self.lines(30, y + 46, 260, 3)
        self.lines(360, y + 46, 200, 3)
        self.lines(640, y + 46, 220, 3)

    def save(self, name):
        body = "\n".join(self.parts)
        (OUT / f"{name}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{self.h}" viewBox="0 0 {W} {self.h}" '
            f'font-family="Segoe UI, Arial, sans-serif">{body}</svg>', encoding="utf-8")


def strona_glowna():
    s = Svg(1390, "Wireframe 1 – strona główna")
    s.header("Start")
    # Hero
    s.rect(30, 90, 940, 260, fill="#dedede")
    s.img(560, 110, 390, 220, "zdjęcie / tło hero")
    s.text(60, 160, "Nagłówek hero", size=26, weight="700", fill="#333")
    s.lines(60, 185, 420, 3)
    s.button(60, 250, 180, 44, "Przycisk CTA")
    s.acf(46, 132, 480, 180, "ACF: nagłówek, opis, CTA (tekst+link)")
    s.acf(560, 110, 390, 220, "ACF: obraz tła")
    # USP
    for i in range(4):
        x = 30 + i * 240
        s.rect(x, 380, 220, 120, fill="#f4f4f4")
        s.rect(x + 90, 395, 40, 40, fill="#d6d6d6", rx=20)
        s.text(x + 110, 458, "Korzyść", size=13, anchor="middle", weight="600")
        s.lines(x + 30, 470, 160, 2, gap=12)
    s.acf(30, 380, 940, 120, "ACF: 4 × korzyść (ikona, tytuł, opis)")
    # Bestsellery
    s.text(30, 545, "Bestsellery", size=18, weight="700", fill="#333")
    for i in range(4):
        x = 30 + i * 240
        s.img(x, 560, 220, 150, "zdjęcie produktu")
        s.lines(x, 722, 180, 2)
        s.text(x, 760, "49,90 zł", size=13, weight="700")
        s.button(x + 120, 744, 100, 28, "Do koszyka")
    s.acf(30, 528, 940, 252, "ACF: wybór produktów (relacja)")
    # Kategorie
    s.text(30, 830, "Kategorie", size=18, weight="700", fill="#333")
    for i, k in enumerate(("Kawa ziarnista", "Kawa mielona", "Akcesoria", "Zestawy")):
        s.img(30 + i * 240, 845, 220, 110, k)
    # Opinie
    s.text(30, 1000, "Opinie klientów", size=18, weight="700", fill="#333")
    for i in range(3):
        x = 30 + i * 320
        s.rect(x, 1015, 300, 100, fill="#f4f4f4")
        s.text(x + 15, 1040, "★★★★★", size=14, fill="#999")
        s.lines(x + 15, 1055, 260, 3)
    s.acf(30, 985, 940, 130, "ACF: opinie (CPT + pola)")
    # Blog
    s.text(30, 1160, "Z bloga – 3 ostatnie wpisy (WP_Query, automatycznie)", size=18, weight="700", fill="#333")
    for i in range(3):
        x = 30 + i * 320
        s.rect(x, 1175, 300, 110, fill="#f4f4f4")
        s.lines(x + 15, 1195, 240, 2)
        s.lines(x + 15, 1235, 260, 3, gap=11)
    s.footer(1300)
    s.save("wireframe_1_strona_glowna")


def kategoria():
    s = Svg(1060, "Wireframe 2 – kategoria produktów")
    s.header("Sklep")
    s.text(30, 95, "Start / Sklep / Kawa ziarnista", size=12, fill="#888")
    s.text(30, 135, "Kawa ziarnista", size=26, weight="700", fill="#333")
    s.lines(30, 150, 600, 2)
    s.acf(26, 112, 640, 50, "ACF: baner i opis kategorii")
    # Filtry
    s.rect(30, 190, 220, 560, fill="#f4f4f4")
    s.text(45, 215, "Filtry", size=15, weight="700")
    y = 240
    for f, n in (("Kraj pochodzenia", 5), ("Stopień palenia", 3), ("Metoda parzenia", 4), ("Cena", 0)):
        s.text(45, y, f, size=12, weight="600")
        y += 14
        for _ in range(n):
            s.rect(45, y, 12, 12, fill="#fff", stroke="#999", rx=2)
            s.lines(64, y + 3, 120, 1)
            y += 20
        if n == 0:
            s.rect(45, y + 4, 190, 6, fill="#cfcfcf", stroke="none", rx=3)
            y += 26
        y += 16
    # Sortowanie i siatka
    s.text(280, 210, "Wyświetlanie 1–9 z 11", size=12, fill="#666")
    s.rect(800, 194, 170, 26, fill="#fff", stroke="#999")
    s.text(812, 212, "Sortuj: popularność ▾", size=12)
    for r in range(3):
        for c in range(3):
            x, y = 280 + c * 232, 240 + r * 172
            s.img(x, y, 212, 100, "produkt")
            s.lines(x, y + 110, 170, 1)
            s.text(x, y + 140, "49,90 zł", size=13, weight="700")
            s.button(x + 112, y + 124, 100, 26, "Do koszyka")
    for i, p in enumerate(("‹", "1", "2", "›")):
        s.rect(500 + i * 40, 770, 32, 30, fill="#fff" if p != "1" else "#555", stroke="#999")
        s.text(516 + i * 40, 790, p, size=12, anchor="middle", fill="#333" if p != "1" else "#fff")
    s.rect(30, 830, 940, 120, fill="#f4f4f4")
    s.text(45, 855, "Poradnik do kategorii (np. jak wybrać kawę ziarnistą)", size=14, weight="600")
    s.lines(45, 870, 880, 4)
    s.acf(30, 830, 940, 120, "ACF: treść SEO pod listą")
    s.footer(970)
    s.save("wireframe_2_kategoria")


def produkt():
    s = Svg(1120, "Wireframe 3 – karta produktu")
    s.header("Sklep")
    s.text(30, 95, "Start / Sklep / Kawa ziarnista / Etiopia Yirgacheffe", size=12, fill="#888")
    s.img(30, 115, 440, 380, "główne zdjęcie produktu")
    for i in range(4):
        s.img(30 + i * 115, 505, 95, 75, "miniatura")
    s.text(510, 150, "Etiopia Yirgacheffe 250 g", size=26, weight="700", fill="#333")
    s.text(510, 178, "★★★★☆  (24 opinie)", size=13, fill="#888")
    s.text(510, 220, "49,90 zł", size=24, weight="700", fill="#333")
    s.lines(510, 240, 440, 3)
    s.text(510, 305, "Profil smaku", size=13, weight="600")
    for i, t in enumerate(("cytrusy", "jaśmin", "herbata")):
        s.rect(510 + i * 95, 315, 85, 26, fill="#f0f0f0", rx=13)
        s.text(552 + i * 95, 333, t, size=11, anchor="middle")
    s.acf(510, 290, 300, 56, "ACF: nuty smakowe")
    s.text(510, 375, "Forma", size=13, weight="600")
    s.rect(510, 385, 200, 32, fill="#fff", stroke="#999")
    s.text(522, 406, "Ziarnista ▾", size=12)
    s.text(730, 375, "Waga", size=13, weight="600")
    s.rect(730, 385, 200, 32, fill="#fff", stroke="#999")
    s.text(742, 406, "250 g ▾", size=12)
    s.rect(510, 440, 90, 44, fill="#fff", stroke="#999")
    s.text(555, 467, "−  1  +", size=13, anchor="middle")
    s.button(615, 440, 315, 44, "Dodaj do koszyka")
    s.text(510, 515, "✓ Wysyłka w 24 h   ✓ Darmowa dostawa od 199 zł", size=12, fill="#666")
    s.text(510, 545, "Data palenia, kraj, wysokość upraw, odmiana – tabela parametrów", size=12, fill="#666")
    s.acf(506, 528, 440, 24, "ACF: parametry kawy")
    # Zakładki
    s.rect(30, 610, 940, 220, fill="#fafafa")
    for i, t in enumerate(("Opis", "Parametry", "Opinie (24)")):
        s.rect(30 + i * 130, 610, 130, 36, fill="#fff" if i == 0 else "#ececec", rx=0)
        s.text(95 + i * 130, 633, t, size=13, anchor="middle", weight="600" if i == 0 else "normal")
    s.lines(50, 670, 880, 7, gap=16)
    s.text(30, 870, "Może Ci się spodobać (produkty powiązane – WooCommerce)", size=18, weight="700", fill="#333")
    for i in range(4):
        x = 30 + i * 240
        s.img(x, 885, 220, 110, "produkt")
        s.lines(x, 1005, 160, 1)
    s.footer(1030)
    s.save("wireframe_3_produkt")


def koszyk():
    s = Svg(900, "Wireframe 4 – koszyk")
    s.header("")
    s.text(30, 115, "Koszyk", size=26, weight="700", fill="#333")
    s.rect(30, 135, 940, 34, fill="#555", stroke="none", rx=6)
    s.text(45, 157, "Brakuje 52,30 zł do darmowej dostawy", size=13, fill="#fff", weight="600")
    s.rect(560, 147, 390, 10, fill="#888", stroke="none", rx=5)
    s.rect(560, 147, 290, 10, fill="#ddd", stroke="none", rx=5)
    s.acf(30, 135, 940, 34, "ACF: próg i komunikat")
    # Tabela
    s.rect(30, 190, 600, 36, fill="#ececec", rx=0)
    for x, t in ((110, "Produkt"), (360, "Cena"), (440, "Ilość"), (540, "Suma")):
        s.text(x, 213, t, size=12, weight="600")
    for i in range(3):
        y = 226 + i * 90
        s.rect(30, y, 600, 90, fill="#fff", rx=0)
        s.img(45, y + 12, 60, 66, "")
        s.lines(120, y + 28, 200, 2)
        s.text(360, y + 50, "49,90 zł", size=12)
        s.rect(430, y + 32, 70, 28, fill="#fff", stroke="#999")
        s.text(465, y + 51, "− 1 +", size=12, anchor="middle")
        s.text(540, y + 50, "49,90 zł", size=12, weight="700")
        s.text(612, y + 50, "×", size=16, fill="#999")
    s.rect(30, 506, 300, 36, fill="#fff", stroke="#999")
    s.text(45, 529, "Kod rabatowy", size=12, fill="#999")
    s.button(340, 506, 140, 36, "Zastosuj", dark=False)
    # Podsumowanie
    s.rect(660, 190, 310, 300, fill="#f4f4f4")
    s.text(680, 220, "Podsumowanie", size=16, weight="700")
    for i, (a, b) in enumerate((("Wartość produktów", "146,70 zł"), ("Wysyłka", "12,99 zł"), ("Rabat", "−0,00 zł"))):
        s.text(680, 260 + i * 30, a, size=13)
        s.text(950, 260 + i * 30, b, size=13, anchor="end")
    s.rect(680, 345, 270, 1, fill="#bbb", stroke="none")
    s.text(680, 380, "Razem", size=16, weight="700")
    s.text(950, 380, "159,69 zł", size=16, weight="700", anchor="end")
    s.button(680, 405, 270, 48, "Przejdź do kasy")
    s.text(815, 475, "BLIK · karta · przelew · pobranie", size=11, anchor="middle", fill="#777")
    s.text(30, 590, "Dobierz do zamówienia (cross-sell WooCommerce)", size=18, weight="700", fill="#333")
    for i in range(4):
        x = 30 + i * 240
        s.img(x, 605, 220, 100, "produkt")
        s.lines(x, 715, 160, 1)
    s.footer(760)
    s.save("wireframe_4_koszyk")


if __name__ == "__main__":
    strona_glowna()
    kategoria()
    produkt()
    koszyk()
    print("OK")
