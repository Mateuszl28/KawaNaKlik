"""Diagramy TO-BE (BPMN) dla procesów zautomatyzowanych w n8n – APPDB Etap II.

Korzysta z generatora bpmn_gen.py (LAB02). Kolory:
  zielony  – krok wykonywany automatycznie przez n8n / system,
  biały    – krok człowieka (zostaje),
  fioletowy – miejsce na AI w kolejnym etapie.

Uruchomienie: python tobe_gen.py <katalog_wyjściowy>
"""

import sys
from pathlib import Path

from bpmn_gen import E, G, Process, T, to_drawio, to_svg

KL, WC, N8, OK_, MG = "Klient", "Sklep (WooCommerce)", "n8n – automatyzacja", "Obsługa klienta", "Magazyn"

TOBE1 = Process(
    "t1", "TO-BE 1 – Realizacja zamówienia",
    [(KL, 110), (WC, 110), (N8, 220), (OK_, 110), (MG, 110)],
    {
        "s": E("start", KL, 0, "Złożenie zamówienia"),
        "t1": T(WC, 1, "Zapis zamówienia, webhook order.created", "auto"),
        "t2": T(N8, 2, "Weryfikacja podpisu HMAC webhooka", "auto"),
        "t3": T(N8, 3, "Normalizacja i walidacja danych", "auto"),
        "g1": G(N8, 4, "Dane kompletne?", lp="above"),
        "t4": T(N8, 5, "Zapis wiersza w arkuszu zamówień", "auto", dy=-62),
        "t5": T(N8, 6, "E-mail z potwierdzeniem do klienta", "auto", dy=-62),
        "t6": T(N8, 7, "Powiadomienie Discord: nowe zamówienie", "auto", dy=-62),
        "t7": T(N8, 5, "Log błędu walidacji", "auto", dy=62),
        "t8": T(OK_, 6, "Kontakt z klientem w sprawie braków", "human"),
        "t9": T(MG, 8, "Kompletacja i pakowanie", "human"),
        "e": E("end", MG, 9, "Paczka gotowa"),
        "e2": E("end", OK_, 7, "Dane uzupełnione"),
    },
    [("s", "t1", "", "right"), ("t1", "t2", "", "right"), ("t2", "t3", "", "right"), ("t3", "g1", "", "right"),
     ("g1", "t4", "tak", "top"), ("t4", "t5", "", "right"), ("t5", "t6", "", "right"), ("t6", "t9", "", "right"),
     ("g1", "t7", "nie", "bottom"), ("t7", "t8", "", "right"), ("t8", "e2", "", "right"), ("t9", "e", "", "right")],
)

SY = "System / harmonogram"
TOBE2 = Process(
    "t2", "TO-BE 2 – Kontrola stanów magazynowych",
    [(SY, 110), (N8, 230), (MG, 110), ("Kierownik operacyjny", 110)],
    {
        "s": E("start", SY, 0, "Codziennie 07:00 (cron)"),
        "t1": T(N8, 1, "Pobranie produktów z API WooCommerce", "auto"),
        "g0": G(N8, 2, "API odpowiada?", lp="above"),
        "t2": T(N8, 3, "Filtr: stan ≤ próg minimalny", "auto", dy=-62),
        "g1": G(N8, 4, "Są niskie stany?", lp="above", dy=-62),
        "t3": T(N8, 5, "Raport e-mail + alert Discord", "auto", dy=-62),
        "t4": T(N8, 5, "Log: wszystko OK", "auto", dy=10),
        "t5": T(N8, 3, "3 ponowienia, potem alert i log błędu", "auto", dy=62),
        "t6": T(MG, 7, "Zamówienie towaru u dostawcy", "human"),
        "t7": T("Kierownik operacyjny", 4, "Sprawdzenie awarii API", "human"),
        "e": E("end", MG, 8, "Towar zamówiony"),
        "e2": E("end", N8, 6, "Koniec", dy=10),
        "e3": E("end", "Kierownik operacyjny", 5, "Awaria zgłoszona"),
    },
    [("s", "t1", "", "right"), ("t1", "g0", "", "right"), ("g0", "t2", "tak", "top"), ("t2", "g1", "", "right"),
     ("g1", "t3", "tak", "right"), ("g1", "t4", "nie", "bottom"), ("t4", "e2", "", "right"),
     ("t3", "t6", "", "right"), ("t6", "e", "", "right"),
     ("g0", "t5", "nie", "bottom"), ("t5", "t7", "", "right"), ("t7", "e3", "", "right")],
)

if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    for p, name in ((TOBE1, "TO-BE_1_realizacja_zamowienia"), (TOBE2, "TO-BE_2_kontrola_stanow")):
        (out / f"{name}.drawio").write_text(to_drawio(p), encoding="utf-8")
        (out / f"{name}.svg").write_text(to_svg(p), encoding="utf-8")
        print(name, p.width, p.height)
