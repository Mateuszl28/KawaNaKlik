# LAB03 – KawaNaKlik

`Sprawozdanie_LAB03_KawaNaKlik.pdf` – sprawozdanie, część 3 (A: APPDB Etap II, B: CMS lab 2).

## APPDB/ – Etap II: Automatyzacja przepływów (bez AI)
- `n8n/` – przepływy do importu (`WF0`–`WF3`, generowane), `eksport/` – eksport z działającej instancji n8n 2.45
  - WF1 – webhook zamówienia WooCommerce (podpis HMAC) → walidacja → arkusz → e-mail → Discord
  - WF2 – kontrola niskich stanów magazynowych (cron 07:00 + GET na żądanie), ponowienia przy awarii API
  - WF3 – obsługa błędów (Error Trigger): log, alert, e-mail
  - WF0 – zastępczy webhook Discorda (zapis wiadomości do pliku)
- `bpmn/` – diagramy TO-BE (`.drawio` + PNG + SVG)
- `kod/` – `n8n_gen.py` (generator przepływów), `tobe_gen.py` + `bpmn_gen.py` (diagramy), `start_n8n.sh`
- `kod/testy/` – `testy_n8n.sh` (przypadki T1–T7, w tym błędne) i skrypty pomocnicze
- `testy/` – wynik testów, arkusz zamówień i logi CSV po testach
- `wordpress/mu-plugins/` – dopuszczenie webhooków WooCommerce na `localhost:5690` (tylko DEV)
- `screeny/` – n8n (przepływy, wykonania), Mailpit, ustawienia webhooka

Uruchomienie: `bash kod/start_n8n.sh` (zmienna `N8N_BIN` wskazuje zainstalowane n8n), import:
`n8n import:workflow --separate --input=n8n`. Poświadczenia (SMTP, WooCommerce) i sekret webhooka
tworzy się lokalnie – nie ma ich w repozytorium.

## CMS/ – Laboratorium 2: ACF, własne typy treści i bloki
- `wp-content/themes/kawanaklik` – motyw 0.2.0: `acf-json/` (6 grup pól), `blocks/` (hero, usp, opinie, faq, blog),
  `inc/post-types.php` (CPT `opinia`, `faq`), `inc/blocks.php` (rejestracja + ograniczenie listy bloków),
  `inc/customizer.php` (dane globalne)
- `kod/seed_lab2.php` – treści przykładowe (opinie, FAQ, strona główna z bloków)
- `diagramy/` – schemat grup pól (generowany z `acf-json`)
- `screeny/` – synchronizacja Local JSON, bloki, CPT, Customizer, test XSS

Wymaga wtyczki Secure Custom Fields (bloki ACF) – po włączeniu motywu: Grupy pól → Synchronizacja.
Wszystkie dane są syntetyczne.
