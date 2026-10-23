"""Generator diagramów BPMN AS-IS dla KawaNaKlik.

Z jednej definicji procesu tworzy:
  * plik .drawio (do edycji w draw.io / diagrams.net),
  * plik .svg (do wstawienia w sprawozdanie, konwertowany potem do PNG).

Uruchomienie: python bpmn_gen.py <katalog_wyjściowy>
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

COL_W = 150          # odstęp między kolumnami
X0 = 120             # środek pierwszej kolumny (po nagłówkach puli i torów)
POOL_HDR = 30
LANE_HDR = 30
TASK_W, TASK_H = 118, 62
EVENT_D = 40
GW_D = 52

FILL = {
    "manual": "#fde3c8",   # ręczne, powtarzalne – kandydat do workflow / RPA
    "ai": "#e6dcf5",       # wymaga rozumienia tekstu – kandydat do AI
    "auto": "#dff0e2",     # już automatyczne (system)
    "human": "#ffffff",    # decyzja człowieka – zostaje
}
STROKE = {"manual": "#c46a1a", "ai": "#6b4fa0", "auto": "#3d8b4f", "human": "#555555"}


def wrap(text, width=17):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines


class Process:
    def __init__(self, key, title, lanes, nodes, edges):
        self.key, self.title = key, title
        self.lanes = lanes          # [(nazwa, wysokość)]
        self.nodes = nodes          # id -> dict(kind, lane, col, label, dy, cat)
        self.edges = edges          # (src, dst, label, exit) exit: right|top|bottom
        self.lane_top = {}
        y = 0
        for name, h in lanes:
            self.lane_top[name] = (y, h)
            y += h
        self.height = y
        self.width = X0 + max(n["col"] for n in nodes.values()) * COL_W + 110

    def center(self, nid):
        n = self.nodes[nid]
        top, h = self.lane_top[n["lane"]]
        return X0 + n["col"] * COL_W, top + h / 2 + n.get("dy", 0)

    def size(self, nid):
        k = self.nodes[nid]["kind"]
        if k == "task":
            return TASK_W, TASK_H
        if k == "gateway":
            return GW_D, GW_D
        return EVENT_D, EVENT_D

    def route(self, src, dst, exit):
        (sx, sy), (tx, ty) = self.center(src), self.center(dst)
        (sw, sh), (tw, th) = self.size(src), self.size(dst)
        if exit in ("top", "bottom"):
            ys = sy - sh / 2 if exit == "top" else sy + sh / 2
            return [(sx, ys), (sx, ty), (tx - tw / 2, ty)]
        start = (sx + sw / 2, sy)
        if abs(sy - ty) < 1:
            return [start, (tx - tw / 2, ty)]
        end_y = ty + th / 2 if ty < sy else ty - th / 2
        return [start, (tx, sy), (tx, end_y)]


# --------------------------------------------------------------------------- SVG

def to_svg(p: Process):
    W, H = p.width, p.height
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W + 2}" height="{H + 2}" '
           f'viewBox="-1 -1 {W + 2} {H + 2}" font-family="Segoe UI, Arial, sans-serif">',
           '<defs><marker id="arr" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" '
           'markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker></defs>',
           f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff" stroke="#333" stroke-width="1.5"/>',
           f'<rect x="0" y="0" width="{POOL_HDR}" height="{H}" fill="#f3eee9" stroke="#333" stroke-width="1.5"/>',
           f'<text transform="translate({POOL_HDR / 2 + 5},{H / 2}) rotate(-90)" text-anchor="middle" '
           f'font-size="13" font-weight="700">KawaNaKlik</text>']
    for name, (top, h) in p.lane_top.items():
        out.append(f'<rect x="{POOL_HDR}" y="{top}" width="{W - POOL_HDR}" height="{h}" fill="none" stroke="#333"/>')
        out.append(f'<rect x="{POOL_HDR}" y="{top}" width="{LANE_HDR}" height="{h}" fill="#faf7f4" stroke="#333"/>')
        lines = wrap(name, 16)
        for i, ln in enumerate(lines):
            off = (i - (len(lines) - 1) / 2) * 13
            out.append(f'<text transform="translate({POOL_HDR + LANE_HDR / 2 + 4 + off},{top + h / 2}) rotate(-90)" '
                       f'text-anchor="middle" font-size="11.5" font-weight="600">{escape(ln)}</text>')

    for s, d, label, exit in p.edges:
        pts = p.route(s, d, exit)
        path = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        out.append(f'<polyline points="{path}" fill="none" stroke="#333" stroke-width="1.3" marker-end="url(#arr)"/>')
        if label:
            (x1, y1), (x2, y2) = pts[0], pts[1]
            if exit == "right":
                lx, ly, anchor = x1 + 6, y1 - 6, "start"
            else:
                lx, ly, anchor = x1 + 6, (y1 + y2) / 2, "start"
            out.append(f'<text x="{lx}" y="{ly}" font-size="10.5" fill="#222" text-anchor="{anchor}" '
                       f'font-style="italic">{escape(label)}</text>')

    for nid, n in p.nodes.items():
        cx, cy = p.center(nid)
        cat = n.get("cat", "human")
        if n["kind"] == "task":
            out.append(f'<rect x="{cx - TASK_W / 2}" y="{cy - TASK_H / 2}" width="{TASK_W}" height="{TASK_H}" rx="9" '
                       f'fill="{FILL[cat]}" stroke="{STROKE[cat]}" stroke-width="1.4"/>')
            lines = wrap(n["label"])
            for i, ln in enumerate(lines):
                off = (i - (len(lines) - 1) / 2) * 12.5
                out.append(f'<text x="{cx}" y="{cy + off + 4}" text-anchor="middle" font-size="10.5">{escape(ln)}</text>')
        elif n["kind"] == "gateway":
            r = GW_D / 2
            out.append(f'<polygon points="{cx},{cy - r} {cx + r},{cy} {cx},{cy + r} {cx - r},{cy}" fill="#fff8d6" '
                       f'stroke="#9a7b00" stroke-width="1.4"/>')
            out.append(f'<text x="{cx}" y="{cy + 6}" text-anchor="middle" font-size="17" font-weight="700" '
                       f'fill="#9a7b00">×</text>')
            lx, ly = (cx - 8, cy - r - 4) if n.get("lp") == "above" else (cx - r - 6, cy + 4)
            out.append(f'<text x="{lx}" y="{ly}" text-anchor="end" font-size="10.5" '
                       f'font-weight="600">{escape(n["label"])}</text>')
        else:
            r = EVENT_D / 2
            sw = 3.5 if n["kind"] == "end" else 1.6
            col = "#b33" if n["kind"] == "end" else "#2e7d32"
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{col}" stroke-width="{sw}"/>')
            lines = wrap(n["label"], 20)
            for i, ln in enumerate(lines):
                y = cy + r + 14 + i * 12 if n["kind"] == "start" else cy - r - 8 - (len(lines) - 1 - i) * 12
                out.append(f'<text x="{cx}" y="{y}" text-anchor="middle" font-size="10">{escape(ln)}</text>')
    out.append("</svg>")
    return "\n".join(out)


# ------------------------------------------------------------------------ draw.io

def to_drawio(p: Process):
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    cells.append(f'<mxCell id="pool" value="KawaNaKlik" style="swimlane;horizontal=0;startSize={POOL_HDR};html=1;'
                 f'fillColor=#f3eee9;" vertex="1" parent="1"><mxGeometry x="0" y="0" width="{p.width}" '
                 f'height="{p.height}" as="geometry"/></mxCell>')
    for i, (name, (top, h)) in enumerate(p.lane_top.items()):
        cells.append(f'<mxCell id="lane{i}" value="{escape(name)}" style="swimlane;horizontal=0;startSize={LANE_HDR};'
                     f'html=1;fillColor=#faf7f4;" vertex="1" parent="pool"><mxGeometry x="{POOL_HDR}" y="{top}" '
                     f'width="{p.width - POOL_HDR}" height="{h}" as="geometry"/></mxCell>')
    for nid, n in p.nodes.items():
        cx, cy = p.center(nid)
        w, h = p.size(nid)
        cat = n.get("cat", "human")
        if n["kind"] == "task":
            style = f"rounded=1;whiteSpace=wrap;html=1;arcSize=14;fillColor={FILL[cat]};strokeColor={STROKE[cat]};fontSize=11;"
            value = n["label"]
        elif n["kind"] == "gateway":
            style = ("shape=mxgraph.bpmn.gateway2;html=1;labelPosition=left;align=right;"
                     "outline=none;symbol=none;gwType=exclusive;fillColor=#fff8d6;strokeColor=#9a7b00;")
            value = n["label"]
        else:
            outline = "end" if n["kind"] == "end" else "standard"
            pos = "bottom;verticalAlign=top" if n["kind"] == "start" else "top;verticalAlign=bottom"
            style = (f"shape=mxgraph.bpmn.event;html=1;verticalLabelPosition={pos};"
                     f"outline={outline};symbol=general;perimeter=ellipsePerimeter;")
            value = n["label"]
        cells.append(f'<mxCell id="{nid}" value="{escape(value)}" style="{style}" vertex="1" parent="1">'
                     f'<mxGeometry x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    for i, (s, d, label, exit) in enumerate(p.edges):
        pts = p.route(s, d, exit)[1:-1]
        waypoints = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in pts)
        cells.append(f'<mxCell id="e{i}" value="{escape(label or "")}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;'
                     f'html=1;endArrow=block;endFill=1;fontStyle=2;" edge="1" parent="1" source="{s}" target="{d}">'
                     f'<mxGeometry relative="1" as="geometry"><Array as="points">{waypoints}</Array></mxGeometry></mxCell>')
    return (f'<mxfile host="app.diagrams.net"><diagram name="{escape(p.title)}" id="{p.key}">'
            f'<mxGraphModel dx="1400" dy="800" grid="1" gridSize="10" guides="1" page="0">'
            f'<root>{"".join(cells)}</root></mxGraphModel></diagram></mxfile>')


# ---------------------------------------------------------------- definicje AS-IS

def T(lane, col, label, cat="human", dy=0):
    return dict(kind="task", lane=lane, col=col, label=label, cat=cat, dy=dy)


def E(kind, lane, col, label, dy=0):
    return dict(kind=kind, lane=lane, col=col, label=label, dy=dy)


def G(lane, col, label, dy=0, lp="left"):
    return dict(kind="gateway", lane=lane, col=col, label=label, dy=dy, lp=lp)


KL, SK, OK_, MG = "Klient", "Sklep (WooCommerce)", "Obsługa klienta", "Magazyn"
P1 = Process(
    "p1", "AS-IS 1 – Realizacja zamówienia",
    [(KL, 110), (SK, 110), (OK_, 185), (MG, 115)],
    {
        "s": E("start", KL, 0, "Złożenie zamówienia"),
        "t1": T(SK, 1, "Zapis zamówienia, e-mail z potwierdzeniem", "auto"),
        "g1": G(OK_, 2, "Płatność?"),
        "t2": T(OK_, 3, "Sprawdzenie wpływu przelewu na wyciągu", "manual", dy=48),
        "t3": T(OK_, 4, "Przepisanie zamówienia do arkusza Excel", "manual"),
        "t4": T(MG, 5, "Wydruk listy kompletacyjnej", "manual"),
        "t5": T(MG, 6, "Kompletacja i pakowanie paczki", "human"),
        "t6": T(MG, 7, "Ręczne utworzenie etykiety w panelu kuriera", "manual"),
        "t7": T(OK_, 8, "Wklejenie nr przesyłki do e-maila dla klienta", "manual"),
        "t8": T(OK_, 9, "Ręczna zmiana statusu na „Zrealizowane”", "manual"),
        "e": E("end", KL, 10, "Paczka u klienta"),
    },
    [("s", "t1", "", "right"), ("t1", "g1", "", "right"),
     ("g1", "t2", "przelew", "bottom"), ("g1", "t3", "pobranie", "right"),
     ("t2", "t3", "", "right"), ("t3", "t4", "", "right"), ("t4", "t5", "", "right"),
     ("t5", "t6", "", "right"), ("t6", "t7", "", "right"), ("t7", "t8", "", "right"),
     ("t8", "e", "", "right")],
)

KI, MG2 = "Kierownik operacyjny", "Magazyn"
P2 = Process(
    "p2", "AS-IS 2 – Obsługa e-maili od klientów",
    [(KL, 110), (OK_, 250), (KI, 110), (MG2, 110)],
    {
        "s": E("start", KL, 0, "E-mail od klienta"),
        "t1": T(OK_, 1, "Przegląd skrzynki (2 razy dziennie)", "manual"),
        "t2": T(OK_, 2, "Ręczne rozpoznanie tematu i pilności", "ai"),
        "t3": T(OK_, 3, "Wyszukanie zamówienia w panelu sklepu", "manual"),
        "g1": G(OK_, 4, "Typ sprawy?", lp="above"),
        "t4": T(OK_, 5, "Odpowiedź pisana od zera", "ai", dy=-80),
        "t5": T(OK_, 5, "Sprawdzenie terminu 14 dni, instrukcja odesłania", "manual"),
        "t6": T(OK_, 5, "Prośba o zdjęcia, oczekiwanie na odpowiedź", "human", dy=80),
        "t7": T(KI, 6, "Decyzja: uznać czy odrzucić reklamację", "human"),
        "t8": T(MG2, 7, "Wysyłka zamiennika / przyjęcie towaru", "human"),
        "t9": T(OK_, 8, "Odpowiedź i ręczny wpis do arkusza zgłoszeń", "manual"),
        "e": E("end", KL, 9, "Klient ma odpowiedź"),
    },
    [("s", "t1", "", "right"), ("t1", "t2", "", "right"), ("t2", "t3", "", "right"),
     ("t3", "g1", "", "right"),
     ("g1", "t4", "pytanie / status", "top"), ("g1", "t5", "zwrot", "right"),
     ("g1", "t6", "reklamacja", "bottom"),
     ("t4", "t9", "", "right"), ("t5", "t9", "", "right"), ("t6", "t7", "", "right"),
     ("t7", "t8", "", "right"), ("t8", "t9", "", "right"), ("t9", "e", "", "right")],
)

DO, AD, WL, BR = "Dostawca", "Administracja", "Właściciel", "Biuro rachunkowe"
P3 = Process(
    "p3", "AS-IS 3 – Obieg faktur kosztowych",
    [(DO, 110), (AD, 180), (WL, 110), (BR, 110)],
    {
        "s": E("start", DO, 0, "Faktura PDF e-mailem"),
        "t1": T(AD, 1, "Pobranie PDF ze skrzynki, zapis na dysku", "manual"),
        "t2": T(AD, 2, "Przepisanie danych faktury do arkusza kosztów", "ai"),
        "t3": T(AD, 3, "Porównanie z zamówieniem i dostawą", "manual"),
        "g1": G(AD, 4, "Zgodna?", lp="above"),
        "t4": T(AD, 5, "Reklamacja faktury u dostawcy", "human", dy=-52),
        "e2": E("end", AD, 6, "Czekamy na korektę", dy=-52),
        "t5": T(WL, 5, "Akceptacja kosztu", "human"),
        "t6": T(WL, 6, "Ręczne zlecenie przelewu w banku", "manual"),
        "t7": T(AD, 7, "Paczka faktur do biura (do 5. dnia)", "manual"),
        "t8": T(BR, 8, "Księgowanie i ewidencja VAT", "human"),
        "e": E("end", BR, 9, "Koszt zaksięgowany"),
    },
    [("s", "t1", "", "right"), ("t1", "t2", "", "right"), ("t2", "t3", "", "right"),
     ("t3", "g1", "", "right"), ("g1", "t4", "nie", "top"), ("t4", "e2", "", "right"),
     ("g1", "t5", "tak", "right"), ("t5", "t6", "", "right"), ("t6", "t7", "", "right"),
     ("t7", "t8", "", "right"), ("t8", "e", "", "right")],
)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    for p in (P1, P2, P3):
        name = {"p1": "AS-IS_1_realizacja_zamowienia", "p2": "AS-IS_2_obsluga_emaili",
                "p3": "AS-IS_3_obieg_faktur"}[p.key]
        (out / f"{name}.drawio").write_text(to_drawio(p), encoding="utf-8")
        (out / f"{name}.svg").write_text(to_svg(p), encoding="utf-8")
        print(name, p.width, p.height)
