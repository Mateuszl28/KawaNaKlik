"""Schemat grup pól ACF motywu KawaNaKlik, generowany z plików acf-json/*.json.

Uruchomienie: python schemat_pol.py <katalog_acf_json>  -> schemat_pol.svg
"""

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

SRC = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent / "schemat_pol.svg"

FORMAT = {
    "image": lambda f: f"zwraca: {f.get('return_format', '')}",
    "link": lambda f: f"zwraca: {f.get('return_format', '')}",
    "post_object": lambda f: f"zwraca: {f.get('return_format', '')} ({', '.join(f.get('post_type', []))})",
    "select": lambda f: f"zwraca: {f.get('return_format', 'value')}",
    "number": lambda f: f"liczba {f.get('min', '')}–{f.get('max', '')}",
    "text": lambda f: "tekst",
    "textarea": lambda f: "tekst",
    "group": lambda f: "tablica pól",
}
LOC = {"block": "Blok", "post_type": "Typ treści"}

ORDER = ["group_knk_blok_hero", "group_knk_blok_usp", "group_knk_blok_opinie", "group_knk_blok_faq",
         "group_knk_blok_blog", "group_knk_opinia"]
groups = [json.loads((SRC / f"{k}.json").read_text(encoding="utf-8")) for k in ORDER]


def rows(group):
    out = []
    for f in group["fields"]:
        out.append((f["name"], f["type"], FORMAT.get(f["type"], lambda _: "")(f), 0))
        if f["type"] == "group":
            for s in f["sub_fields"]:
                out.append((s["name"], s["type"], FORMAT.get(s["type"], lambda _: "")(s), 1))
    return out


COLW, ROWH, HEAD, GAP = 460, 21, 52, 24
cols = [[], []]
heights = [0, 0]
for g in groups:
    h = HEAD + len(rows(g)) * ROWH + 22
    i = 0 if heights[0] <= heights[1] else 1
    cols[i].append((g, heights[i]))
    heights[i] += h + GAP
W, H = 2 * COLW + 3 * GAP, max(heights) + GAP + 40

p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
     f'font-family="Segoe UI, Arial, sans-serif"><rect width="{W}" height="{H}" fill="#fff"/>',
     f'<text x="{GAP}" y="30" font-size="17" font-weight="700" fill="#4a2a19">Grupy pól ACF – motyw KawaNaKlik '
     f'(źródło: acf-json/)</text>']
for ci, col in enumerate(cols):
    x = GAP + ci * (COLW + GAP)
    for g, y0 in col:
        y = y0 + 50
        r = rows(g)
        h = HEAD + len(r) * ROWH + 22
        loc = g["location"][0][0]
        p.append(f'<rect x="{x}" y="{y}" width="{COLW}" height="{h}" rx="8" fill="#faf7f4" stroke="#6b3e26"/>')
        p.append(f'<rect x="{x}" y="{y}" width="{COLW}" height="30" rx="8" fill="#6b3e26"/>')
        p.append(f'<rect x="{x}" y="{y + 20}" width="{COLW}" height="10" fill="#6b3e26"/>')
        p.append(f'<text x="{x + 12}" y="{y + 20}" font-size="13.5" font-weight="700" fill="#fff">{escape(g["title"])}</text>')
        p.append(f'<text x="{x + COLW - 12}" y="{y + 20}" font-size="11" fill="#f3e6d8" text-anchor="end">'
                 f'{escape(LOC.get(loc["param"], loc["param"]))} = {escape(loc["value"])}</text>')
        p.append(f'<text x="{x + 12}" y="{y + 46}" font-size="10.5" font-weight="700" fill="#555">nazwa pola</text>'
                 f'<text x="{x + 175}" y="{y + 46}" font-size="10.5" font-weight="700" fill="#555">typ</text>'
                 f'<text x="{x + 270}" y="{y + 46}" font-size="10.5" font-weight="700" fill="#555">format / wartość w PHP</text>')
        for j, (name, typ, fmt, ind) in enumerate(r):
            yy = y + HEAD + 16 + j * ROWH
            if j % 2 == 0:
                p.append(f'<rect x="{x + 1}" y="{yy - 14}" width="{COLW - 2}" height="{ROWH}" fill="#f1ebe4"/>')
            p.append(f'<text x="{x + 12 + ind * 16}" y="{yy}" font-size="11.5" font-family="Consolas, monospace" '
                     f'fill="#1f1a17">{"└ " if ind else ""}{escape(name)}</text>')
            p.append(f'<text x="{x + 175}" y="{yy}" font-size="11.5" fill="#1f1a17">{escape(typ)}</text>')
            p.append(f'<text x="{x + 270}" y="{yy}" font-size="11" fill="#555">{escape(fmt)}</text>')
p.append("</svg>")
OUT.write_text("\n".join(p), encoding="utf-8")
print(OUT, W, H)
