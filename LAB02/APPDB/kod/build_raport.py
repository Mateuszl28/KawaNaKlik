"""Składa sprawozdanie LAB02 (HTML) i liczy wskaźniki bazowe z wygenerowanych danych.

Uruchomienie (z katalogu LAB02): python kod/build_raport.py
Wynik: sprawozdanie_LAB02.html (PDF robiony potem przez headless Chrome).
"""

import csv
import html
from collections import Counter
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
DANE = ROOT / "dane"


def wczytaj(nazwa):
    with open(DANE / f"{nazwa}.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def zl(x, dec=0):
    s = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")
    return f"{s} zł"


def num(x, dec=0):
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")


def e(x):
    return html.escape(str(x))


def tabela(wiersze, kolumny, naglowki=None, skroc=None):
    skroc = skroc or {}
    h = "".join(f"<th>{e(n)}</th>" for n in (naglowki or kolumny))
    body = ""
    for w in wiersze:
        komorki = []
        for k in kolumny:
            v = str(w[k])
            if k in skroc and len(v) > skroc[k]:
                v = v[: skroc[k]].rstrip() + "…"
            komorki.append(f"<td>{e(v)}</td>")
        body += "<tr>" + "".join(komorki) + "</tr>"
    return f"<table class=data><tr>{h}</tr>{body}</table>"


kl, prod, zam, poz, mail, fv = (wczytaj(n) for n in
                                ("klienci", "produkty", "zamowienia", "pozycje_zamowien", "emaile", "faktury"))

# ------------------------------------------------------------------ statystyki
dni = Counter(z["data"][:10] for z in zam)
n_dni = len(dni)
zam_dzien = len(zam) / n_dni
aov = mean(float(z["razem"]) for z in zam)
udzial_przelew = sum(z["platnosc"] == "przelew tradycyjny" for z in zam) / len(zam)
bledy = [z for z in zam if z["blad_reczny"]]
stopa_bledow = len(bledy) / len(zam)
bledy_typy = Counter(z["blad_reczny"] for z in bledy)
kat_mail = Counter(m["kategoria_wzorcowa"] for m in mail)
udzial_reklamacji = kat_mail["reklamacja"] / len(mail)

# ---------------------------------------------------------- założenia kosztowe
NARZUT = 1.2048          # koszty pracodawcy (ZUS, FP, FGŚP, PPK) – przybliżenie
GODZ = 168               # godzin pracy w miesiącu
STAWKI = {               # pensja brutto miesięcznie
    "Obsługa klienta": 6500, "Magazyn": 5400, "Administracja": 6000, "Kierownik operacyjny": 7500,
}
RBH = {k: round(v * NARZUT / GODZ) for k, v in STAWKI.items()}
RBH["Właściciel"] = 80   # wycena czasu właściciela
DNI_MIES = 30
ZAM_MIES = zam_dzien * DNI_MIES
MAIL_DZIEN = 55
MAIL_MIES = MAIL_DZIEN * DNI_MIES
FV_MIES = 45
KOSZT_BLEDU = 38         # ponowna wysyłka + rabat/towar + ok. 20 min pracy

# czasy AS-IS w minutach (szacunek z obserwacji procesu)
ZAM_KROKI = [
    ("Sprawdzenie wpływu przelewu (tylko przelewy)", "Obsługa klienta", 1.5 * udzial_przelew),
    ("Przepisanie zamówienia do arkusza", "Obsługa klienta", 2.5),
    ("Wydruk listy kompletacyjnej", "Magazyn", 0.3),
    ("Ręczne utworzenie etykiety kurierskiej", "Magazyn", 2.0),
    ("Wklejenie nr przesyłki do e-maila", "Obsługa klienta", 1.2),
    ("Ręczna zmiana statusu", "Obsługa klienta", 0.4),
]
MAIL_KROKI = [
    ("Przegląd skrzynki", "Obsługa klienta", 0.5),
    ("Rozpoznanie tematu i pilności", "Obsługa klienta", 1.0),
    ("Wyszukanie zamówienia", "Obsługa klienta", 2.0),
    ("Napisanie odpowiedzi (średnio)", "Obsługa klienta", 5.0),
    ("Wpis do arkusza zgłoszeń", "Obsługa klienta", 1.0),
    ("Decyzja kierownika (tylko reklamacje)", "Kierownik operacyjny", 5.0 * udzial_reklamacji),
]
FV_KROKI = [
    ("Pobranie PDF i zapis na dysku", "Administracja", 1.0),
    ("Przepisanie danych do arkusza", "Administracja", 4.0),
    ("Porównanie z zamówieniem i dostawą", "Administracja", 4.0),
    ("Akceptacja kosztu", "Właściciel", 1.0),
    ("Zlecenie przelewu", "Właściciel", 2.0),
    ("Paczka faktur do biura (rozłożona)", "Administracja", 1.0),
]


def koszt_procesu(kroki, wolumen):
    minuty = sum(m for _, _, m in kroki)
    koszt_jedn = sum(m / 60 * RBH[rola] for _, rola, m in kroki)
    return minuty, koszt_jedn, wolumen * minuty / 60, wolumen * koszt_jedn


ZP = koszt_procesu(ZAM_KROKI, ZAM_MIES)
MP = koszt_procesu(MAIL_KROKI, MAIL_MIES)
FP = koszt_procesu(FV_KROKI, FV_MIES)
BLEDY_MIES = stopa_bledow * ZAM_MIES
KOSZT_BLEDOW = BLEDY_MIES * KOSZT_BLEDU
RAZEM_H = ZP[2] + MP[2] + FP[2]
RAZEM_ZL = ZP[3] + MP[3] + FP[3] + KOSZT_BLEDOW


def kroki_html(kroki):
    return "".join(f"<tr><td>{e(n)}</td><td>{e(r)}</td><td class=r>{num(m, 2)}</td>"
                   f"<td class=r>{zl(m / 60 * RBH[r], 2)}</td></tr>" for n, r, m in kroki)


# ------------------------------------------------------------ ocena kandydatów
# (proces, zadanie, P, C, R, H, typ, rekomendacja)
OCENA = [
    ("Zamówienie", "Sprawdzenie wpływu przelewu", 5, 3, 4, 1, "workflow", "Automatyzować – dopasowanie wyciągu / bramka płatności"),
    ("Zamówienie", "Przepisanie zamówienia do arkusza", 5, 4, 4, 1, "workflow", "Automatyzować – webhook WooCommerce → arkusz"),
    ("Zamówienie", "Wydruk listy kompletacyjnej", 5, 2, 2, 1, "workflow", "Automatyzować w pakiecie (PDF generowany sam)"),
    ("Zamówienie", "Kompletacja i pakowanie", 5, 5, 3, 5, "—", "Zostaje człowiek – praca fizyczna (wsparcie: skaner EAN)"),
    ("Zamówienie", "Utworzenie etykiety kurierskiej", 5, 4, 4, 1, "workflow/API", "Automatyzować – API przewoźnika"),
    ("Zamówienie", "Nr przesyłki w e-mailu do klienta", 5, 3, 3, 1, "workflow", "Automatyzować"),
    ("Zamówienie", "Zmiana statusu zamówienia", 5, 1, 2, 1, "workflow", "Automatyzować w pakiecie z etykietą"),
    ("E-maile", "Przegląd skrzynki", 5, 2, 3, 1, "workflow", "Automatyzować – wyzwalacz IMAP"),
    ("E-maile", "Rozpoznanie tematu i pilności", 5, 3, 3, 3, "AI", "AI klasyfikuje, człowiek przy niskiej pewności"),
    ("E-maile", "Wyszukanie zamówienia", 5, 3, 2, 1, "workflow", "Automatyzować – nr zamówienia / e-mail → API"),
    ("E-maile", "Odpowiedź na pytanie / status", 4, 4, 3, 3, "AI", "AI szkicuje, człowiek zatwierdza"),
    ("E-maile", "Sprawdzenie terminu zwrotu", 4, 2, 4, 2, "workflow", "Automatyzować – reguła 14 dni"),
    ("E-maile", "Decyzja o reklamacji", 3, 3, 4, 5, "—", "Zostaje człowiek (AI: streszczenie sprawy)"),
    ("E-maile", "Wpis do arkusza zgłoszeń", 5, 2, 3, 1, "workflow", "Automatyzować"),
    ("Faktury", "Pobranie PDF ze skrzynki", 5, 1, 2, 1, "workflow", "Automatyzować w pakiecie"),
    ("Faktury", "Przepisanie danych faktury", 5, 4, 4, 2, "AI", "AI odczytuje PDF, walidacja sum regułami"),
    ("Faktury", "Porównanie z zamówieniem", 5, 4, 4, 3, "workflow + AI", "Automatyzować, wyjątki do człowieka"),
    ("Faktury", "Akceptacja kosztu", 4, 1, 2, 5, "—", "Zostaje człowiek – 1 klik w powiadomieniu"),
    ("Faktury", "Zlecenie przelewu", 4, 2, 4, 4, "częściowo", "Paczka przelewów, zatwierdza właściciel"),
    ("Faktury", "Paczka faktur do biura", 5, 2, 3, 1, "workflow", "Automatyzować – folder współdzielony"),
]


def wynik(p, c, r, h):
    return p + c + r + (6 - h)


ocena_html = ""
for proc, zad, p, c, r, h, typ, rek in sorted(OCENA, key=lambda o: -wynik(*o[2:6])):
    w = wynik(p, c, r, h)
    klasa = "hi" if w >= 15 and h <= 3 else ("mid" if w >= 13 else "lo")
    ocena_html += (f"<tr class={klasa}><td>{e(proc)}</td><td>{e(zad)}</td><td class=c>{p}</td><td class=c>{c}</td>"
                   f"<td class=c>{r}</td><td class=c>{h}</td><td class=c><b>{w}</b></td><td>{e(typ)}</td>"
                   f"<td>{e(rek)}</td></tr>")

# ------------------------------------------------------------------ próbki
probka_kl = tabela(kl[:4], ["klient_id", "imie", "nazwisko", "email", "miasto", "typ", "zgoda_marketing"])
probka_prod = tabela(prod[:6], ["sku", "nazwa", "kategoria", "cena_brutto", "stan_magazynowy"])
probka_zam = tabela(zam[:6], ["nr_zamowienia", "data", "klient_id", "status", "platnosc", "wysylka", "razem", "blad_reczny"])
probka_mail = tabela([m for m in mail if m["kategoria_wzorcowa"] in
                      ("reklamacja", "zwrot", "status_przesylki", "spam", "wiele_spraw", "faktura")][:7],
                     ["email_id", "temat", "tresc", "kategoria_wzorcowa", "priorytet_wzorcowy", "ton"],
                     skroc={"tresc": 150})
fv_html = tabela(fv, ["nr_faktury", "dostawca", "data_wystawienia", "termin_platnosci", "brutto", "uwagi"])
kat_html = "".join(f"<tr><td>{e(k)}</td><td class=r>{v}</td></tr>" for k, v in kat_mail.most_common())
tony = sorted({m["ton"] for m in mail})
bledy_html = "".join(f"<tr><td>{e(k)}</td><td class=r>{v}</td></tr>" for k, v in bledy_typy.most_common())

ARKUSZE = [
    ("klienci", len(kl), "id, imię, nazwisko, e-mail (.test), telefon, miasto, adres, typ (osoba/firma), zgoda marketingowa, data rejestracji"),
    ("produkty", len(prod), "SKU, nazwa, kategoria, cena brutto, stan magazynowy, waga"),
    ("zamowienia", len(zam), f"nr, data i godzina, klient, status, płatność, wysyłka, wartości, błąd ręczny – {n_dni} dni (1–14.10.2026)"),
    ("pozycje_zamowien", len(poz), "nr zamówienia, SKU, produkt, ilość, cena, wartość"),
    ("emaile", len(mail), "id, data, nadawca, klient, nr zamówienia, temat, treść, kategoria i priorytet wzorcowy, ton"),
    ("faktury", len(fv), "nr, dostawca, NIP (fikcyjny), daty, netto/VAT/brutto, plik PDF, uwagi"),
]
arkusze_html = "".join(f"<tr><td><code>{a}</code></td><td class=r>{num(n)}</td><td>{e(o)}</td></tr>" for a, n, o in ARKUSZE)

rbh_html = "".join(f"<tr><td>{e(k)}</td><td class=r>{zl(STAWKI[k]) if k in STAWKI else '—'}</td>"
                   f"<td class=r>{zl(v)}/h</td></tr>" for k, v in RBH.items())

szablon = (ROOT / "kod" / "szablon_raportu.html").read_text(encoding="utf-8")
podstaw = dict(
    ZAM_LICZBA=num(len(zam)), ZAM_DZIEN=num(zam_dzien, 0), ZAM_MIN=min(dni.values()), ZAM_MAX=max(dni.values()),
    AOV=zl(aov, 2), OBROT=zl(sum(float(z["razem"]) for z in zam)), KLIENCI=num(len(kl)),
    KLIENCI_AKTYWNI=num(len({z["klient_id"] for z in zam})), PRZELEW=num(udzial_przelew * 100, 0),
    ARKUSZE=arkusze_html, PROBKA_KL=probka_kl, PROBKA_PROD=probka_prod, PROBKA_ZAM=probka_zam,
    PROBKA_MAIL=probka_mail, FV=fv_html, KAT=kat_html, TONY=", ".join(tony), N_TONY=len(tony),
    OCENA=ocena_html, RBH=rbh_html,
    ZAM_KROKI=kroki_html(ZAM_KROKI), MAIL_KROKI=kroki_html(MAIL_KROKI), FV_KROKI=kroki_html(FV_KROKI),
    ZP_MIN=num(ZP[0], 1), ZP_JEDN=zl(ZP[1], 2), ZP_H=num(ZP[2]), ZP_ZL=zl(ZP[3]), ZAM_MIES=num(ZAM_MIES),
    MP_MIN=num(MP[0], 1), MP_JEDN=zl(MP[1], 2), MP_H=num(MP[2]), MP_ZL=zl(MP[3]), MAIL_MIES=num(MAIL_MIES),
    MAIL_DZIEN=MAIL_DZIEN,
    FP_MIN=num(FP[0], 1), FP_JEDN=zl(FP[1], 2), FP_H=num(FP[2], 1), FP_ZL=zl(FP[3]), FV_MIES=FV_MIES,
    BLEDY_N=len(bledy), BLEDY_PROC=num(stopa_bledow * 100, 2), BLEDY_MIES=num(BLEDY_MIES),
    KOSZT_BLEDU=zl(KOSZT_BLEDU), KOSZT_BLEDOW=zl(KOSZT_BLEDOW), BLEDY_TYPY=bledy_html,
    RAZEM_H=num(RAZEM_H), RAZEM_ZL=zl(RAZEM_ZL), RAZEM_ROK=zl(RAZEM_ZL * 12), ETATY=num(RAZEM_H / GODZ, 1),
    REKLAMACJE_PROC=num(udzial_reklamacji * 100),
)
for k, v in podstaw.items():
    szablon = szablon.replace("{{" + k + "}}", str(v))
assert "{{" not in szablon, szablon[szablon.index("{{"):szablon.index("{{") + 40]
(ROOT / "sprawozdanie_LAB02.html").write_text(szablon, encoding="utf-8")
print("OK", {k: podstaw[k] for k in ("ZAM_DZIEN", "ZP_ZL", "MP_ZL", "FP_ZL", "KOSZT_BLEDOW", "RAZEM_ZL", "RAZEM_H", "ETATY")})
