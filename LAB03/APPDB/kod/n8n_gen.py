"""Generator przepływów n8n (JSON do importu) – APPDB Etap II, KawaNaKlik.

WF0  Mock Discord (test)           – udaje webhook Discorda, zapisuje wiadomości do pliku
WF1  Zamówienie → arkusz → e-mail → Discord   (webhook WooCommerce, podpis HMAC, walidacja)
WF2  Kontrola stanów magazynowych (cron 07:00 + uruchomienie na żądanie, retry, obsługa awarii API)
WF3  Obsługa błędów (Error Trigger)  – log + alert dla każdego nieobsłużonego błędu

Sekrety NIE są w plikach: sekret webhooka czytany z $env.WC_WEBHOOK_SECRET, adres Discorda
z $env.DISCORD_WEBHOOK_URL (domyślnie mock), dane SMTP i klucze WooCommerce – w poświadczeniach n8n.

Uruchomienie: python n8n_gen.py <katalog_plików_n8n> <katalog_wyjściowy_json>
"""

import json
import sys
from pathlib import Path

FILES = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "C:/Users/lagoc/.n8n-kawanaklik/pliki"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else ".")

SMTP = {"smtp": {"id": "KNKsmtpMailpit01", "name": "Mailpit (lokalny SMTP)"}}
WOO = {"wooCommerceApi": {"id": "KNKwooCommerce01", "name": "WooCommerce KawaNaKlik (test)"}}
DISCORD_URL = "={{ $env.DISCORD_WEBHOOK_URL || 'http://localhost:5690/webhook/discord-mock' }}"
NOW = "={{ $now.toFormat('yyyy-LL-dd HH:mm:ss') }}"


class WF:
    def __init__(self, wid, name, error_wf=None):
        self.wid, self.name, self.nodes, self.conn = wid, name, [], {}
        # executionTimeout: zawieszony węzeł (np. SMTP) nie blokuje wykonania w nieskończoność
        self.settings = {"executionOrder": "v1", "saveManualExecutions": True, "executionTimeout": 120}
        if error_wf:
            self.settings["errorWorkflow"] = error_wf

    def node(self, name, type_, ver, x, y, params, **extra):
        n = {"parameters": params, "id": f"{self.wid}-{len(self.nodes):02d}", "name": name,
             "type": f"n8n-nodes-base.{type_}", "typeVersion": ver, "position": [x, y]}
        n.update(extra)
        self.nodes.append(n)
        return name

    def link(self, a, b, out=0):
        self.conn.setdefault(a, {"main": []})
        while len(self.conn[a]["main"]) <= out:
            self.conn[a]["main"].append([])
        self.conn[a]["main"][out].append({"node": b, "type": "main", "index": 0})

    def chain(self, *names):
        for a, b in zip(names, names[1:]):
            self.link(a, b)

    def dump(self, fname):
        data = {"id": self.wid, "name": self.name, "nodes": self.nodes, "connections": self.conn,
                "settings": self.settings, "active": False, "pinData": {}, "tags": []}
        (OUT / fname).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def set_node(wf, name, x, y, fields):
    """Węzeł Edit Fields (Set) z listą (nazwa, wyrażenie, typ)."""
    return wf.node(name, "set", 3.4, x, y, {
        "assignments": {"assignments": [
            {"id": f"{name}-{i}", "name": k, "value": v, "type": t} for i, (k, v, t) in enumerate(fields)]},
        "options": {}})


CSV_LINE_JS = """// Jeden wiersz CSV (separator ;) na element – bez BOM i z końcem linii, żeby dopisywanie nie sklejało wierszy.
const esc = v => {
  const s = v === null || v === undefined ? '' : String(v);
  return /[";\\r\\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};
return $input.all().map(item => ({
  json: item.json,
  binary: { data: {
    data: Buffer.from(Object.values(item.json).map(esc).join(';') + '\\r\\n', 'utf8').toString('base64'),
    mimeType: 'text/csv', fileName: 'wiersz.csv' } },
}));"""


def append_csv(wf, prefix, x, y, filename):
    """Code (wiersz CSV jako plik binarny) + zapis z dopisywaniem do pliku – „arkusz” w pliku CSV."""
    a = wf.node(f"{prefix}: do CSV", "code", 2, x, y, {"jsCode": CSV_LINE_JS})
    b = wf.node(f"{prefix}: dopisz do pliku", "readWriteFile", 1, x + 220, y,
                {"operation": "write", "fileName": f"{FILES}/{filename}", "options": {"append": True}})
    wf.link(a, b)
    return a, b


def discord(wf, name, x, y, content_expr):
    return wf.node(name, "httpRequest", 4.2, x, y, {
        "method": "POST", "url": DISCORD_URL, "sendBody": True, "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ username: 'KawaNaKlik – automaty', content: " + content_expr + " }) }}",
        "options": {"timeout": 5000}},
        retryOnFail=True, maxTries=2, waitBetweenTries=1000, onError="continueRegularOutput")


def email(wf, name, x, y, to, subject, html):
    return wf.node(name, "emailSend", 2.1, x, y, {
        "fromEmail": "KawaNaKlik <sklep@kawanaklik.test>", "toEmail": to, "subject": subject,
        "emailFormat": "html", "html": html, "options": {"appendAttribution": False}},
        credentials=SMTP, onError="continueRegularOutput")


def respond(wf, name, x, y, code, body):
    return wf.node(name, "respondToWebhook", 1.1, x, y, {
        "respondWith": "json", "responseBody": body, "options": {"responseCode": code}})


def if_node(wf, name, x, y, left, op, right=None, typ="string"):
    cond = {"id": f"{name}-c", "leftValue": left, "operator": {"type": typ, "operation": op}}
    if right is not None:
        cond["rightValue"] = right
    if op in ("true", "false", "empty", "notEmpty"):
        cond["operator"]["singleValue"] = True
    return wf.node(name, "if", 2.2, x, y, {
        "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                       "conditions": [cond], "combinator": "and"}, "options": {}})


# ------------------------------------------------------------------------------------- WF0
wf0 = WF("KNKmockDiscord01", "WF0 – Mock Discord (test)")
w = wf0.node("Webhook Discord (mock)", "webhook", 2, 0, 0,
             {"httpMethod": "POST", "path": "discord-mock", "responseMode": "onReceived", "options": {}},
             webhookId="knk-discord-mock")
s = set_node(wf0, "Wiadomość", 220, 0, [("czas", NOW, "string"), ("nadawca", "={{ $json.body.username }}", "string"),
                                         ("tresc", "={{ $json.body.content }}", "string")])
c, f = append_csv(wf0, "Log Discord", 440, 0, "discord_mock.csv")
wf0.chain(w, s, c)
wf0.dump("WF0_mock_discord.json")

# ------------------------------------------------------------------------------------- WF1
VERIFY = r"""// Weryfikacja podpisu WooCommerce (HMAC-SHA256, base64) i normalizacja danych zamówienia.
const crypto = require('crypto');
const SECRET = $env.WC_WEBHOOK_SECRET || '';
const item = $input.first();
const headers = item.json.headers || {};
const body = item.json.body || {};

// WooCommerce wysyła „ping” (webhook_id=…) przy zapisie webhooka.
if (body.webhook_id && !body.id) {
  return [{ json: { status: 'ping', webhook_id: body.webhook_id } }];
}

const signature = headers['x-wc-webhook-signature'] || '';
const raw = item.binary && item.binary.data
  ? (await this.helpers.getBinaryDataBuffer(0, 'data')).toString('utf8')
  : JSON.stringify(body);
const expected = crypto.createHmac('sha256', SECRET).update(raw).digest('base64');
const valid = SECRET !== '' && signature.length === expected.length &&
  crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
if (!valid) {
  return [{ json: { status: 'bad_signature', powod: signature ? 'nieprawidłowy podpis' : 'brak podpisu',
    topic: headers['x-wc-webhook-topic'] || '-', zamowienie: String(body.number || body.id || '-') } }];
}

// Test obsługi błędów: notatka „#TEST-BLAD” wywołuje wyjątek → przepływ WF3.
if ((body.customer_note || '').includes('#TEST-BLAD')) {
  throw new Error(`Symulowany błąd przetwarzania zamówienia ${body.number} (test WF3)`);
}

const b = body.billing || {};
const order = {
  numer: String(body.number || body.id || ''),
  data: body.date_created || '',
  klient: `${b.first_name || ''} ${b.last_name || ''}`.trim(),
  email: (b.email || '').trim(),
  telefon: b.phone || '',
  adres: [b.address_1, b.postcode, b.city].filter(Boolean).join(', '),
  pozycje: (body.line_items || []).map(li => `${li.quantity}× ${li.name}`).join('; '),
  liczba_pozycji: (body.line_items || []).length,
  razem: Number(body.total || 0),
  waluta: body.currency || 'PLN',
  platnosc: body.payment_method_title || '',
  status: body.status || '',
};

const problemy = [];
if (!order.email) problemy.push('brak adresu e-mail');
else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(order.email)) problemy.push('niepoprawny adres e-mail');
if (!order.klient) problemy.push('brak imienia i nazwiska');
if (!b.address_1 || !b.city || !b.postcode) problemy.push('niepełny adres');
if (order.liczba_pozycji === 0) problemy.push('brak pozycji w zamówieniu');
if (!(order.razem > 0)) problemy.push('kwota zamówienia ≤ 0');

return [{ json: { status: 'ok', order, problemy, poprawne: problemy.length === 0 } }];"""

O = "$('Weryfikacja i normalizacja').first().json"
wf1 = WF("KNKzamowienie001", "WF1 – Zamówienie → arkusz → e-mail → Discord", error_wf="KNKobslugaBledow")
w = wf1.node("Webhook: nowe zamówienie (WooCommerce)", "webhook", 2, 0, 200,
             {"httpMethod": "POST", "path": "zamowienie", "responseMode": "responseNode", "options": {"rawBody": True}},
             webhookId="knk-zamowienie")
v = wf1.node("Weryfikacja i normalizacja", "code", 2, 240, 200, {"jsCode": VERIFY})
ping = if_node(wf1, "Ping?", 480, 200, "={{ $json.status }}", "equals", "ping")
r_ping = respond(wf1, "Odpowiedź: pong", 720, 40, 200, "={{ { ok: true, ping: true } }}")
sig = if_node(wf1, "Podpis poprawny?", 720, 260, "={{ $json.status }}", "equals", "ok")
dane = if_node(wf1, "Dane kompletne?", 960, 160, "={{ $json.poprawne }}", "true", typ="boolean")

# Ścieżka OK
row = set_node(wf1, "Wiersz arkusza", 1200, 0, [
    ("zapisano", NOW, "string"), ("numer", f"={{{{ {O}.order.numer }}}}", "string"),
    ("data_zamowienia", f"={{{{ {O}.order.data }}}}", "string"), ("klient", f"={{{{ {O}.order.klient }}}}", "string"),
    ("email", f"={{{{ {O}.order.email }}}}", "string"), ("telefon", f"={{{{ {O}.order.telefon }}}}", "string"),
    ("adres", f"={{{{ {O}.order.adres }}}}", "string"), ("pozycje", f"={{{{ {O}.order.pozycje }}}}", "string"),
    ("razem", f"={{{{ {O}.order.razem.toFixed(2) }}}}", "string"), ("waluta", f"={{{{ {O}.order.waluta }}}}", "string"),
    ("platnosc", f"={{{{ {O}.order.platnosc }}}}", "string"), ("status", f"={{{{ {O}.order.status }}}}", "string")])
c1, f1 = append_csv(wf1, "Arkusz zamówień", 1420, 0, "arkusz_zamowien.csv")
mail_ok = email(wf1, "E-mail: potwierdzenie do klienta", 2080, 0, f"={{{{ {O}.order.email }}}}",
                f"=Potwierdzenie zamówienia nr {{{{ {O}.order.numer }}}} – KawaNaKlik",
                f"=<h2>Dziękujemy za zamówienie!</h2><p>Dzień dobry {{{{ {O}.order.klient }}}},</p>"
                f"<p>przyjęliśmy zamówienie <b>nr {{{{ {O}.order.numer }}}}</b> na kwotę "
                f"<b>{{{{ {O}.order.razem.toFixed(2) }}}} {{{{ {O}.order.waluta }}}}</b>.</p>"
                f"<p>Produkty: {{{{ {O}.order.pozycje }}}}<br>Adres dostawy: {{{{ {O}.order.adres }}}}<br>"
                f"Płatność: {{{{ {O}.order.platnosc }}}}</p><p>Zamówienia złożone do 13:00 wysyłamy tego samego dnia."
                f"</p><p>Zespół KawaNaKlik</p>")
d_ok = discord(wf1, "Discord: nowe zamówienie", 2300, 0,
               f"`🛒 Nowe zamówienie nr ${{{O}.order.numer}} – ${{{O}.order.klient}}, ${{{O}.order.razem.toFixed(2)}} zł (${{{O}.order.platnosc}})`")
r_ok = respond(wf1, "Odpowiedź: 200 OK", 1860, 0, 200, f"={{{{ {{ ok: true, zamowienie: {O}.order.numer }} }}}}")

# Ścieżka: dane niekompletne
err_row = set_node(wf1, "Wiersz logu: walidacja", 1200, 300, [
    ("czas", NOW, "string"), ("zrodlo", "WF1 – walidacja zamówienia", "string"),
    ("opis", f"={{{{ 'Zamówienie ' + {O}.order.numer + ': ' + {O}.problemy.join(', ') }}}}", "string"),
    ("szczegoly", f"={{{{ {O}.order.klient + ' <' + {O}.order.email + '>' }}}}", "string")])
c2, f2 = append_csv(wf1, "Log błędów (walidacja)", 1420, 300, "log_bledow.csv")
mail_err = email(wf1, "E-mail: alert do obsługi", 2080, 300, "obsluga@kawanaklik.test",
                 f"=⚠ Zamówienie {{{{ {O}.order.numer }}}} wymaga uzupełnienia danych",
                 f"=<p>Zamówienie <b>{{{{ {O}.order.numer }}}}</b> nie przeszło walidacji:</p>"
                 f"<ul><li>{{{{ {O}.problemy.join('</li><li>') }}}}</li></ul>"
                 f"<p>Klient: {{{{ {O}.order.klient || '(brak)' }}}}, e-mail: {{{{ {O}.order.email || '(brak)' }}}}, "
                 f"tel.: {{{{ {O}.order.telefon || '(brak)' }}}}</p><p>Skontaktuj się z klientem przed wysyłką.</p>")
d_err = discord(wf1, "Discord: zamówienie do uzupełnienia", 2300, 300,
                f"`⚠️ Zamówienie ${{{O}.order.numer}} nie przeszło walidacji: ${{{O}.problemy.join(', ')}}`")
r_422 = respond(wf1, "Odpowiedź: 422", 1860, 300, 422, f"={{{{ {{ ok: false, problemy: {O}.problemy }} }}}}")

# Ścieżka: zły podpis
bad_row = set_node(wf1, "Wiersz logu: podpis", 960, 480, [
    ("czas", NOW, "string"), ("zrodlo", "WF1 – webhook zamówień", "string"),
    ("opis", "={{ 'Odrzucono webhook: ' + $json.powod }}", "string"),
    ("szczegoly", "={{ 'topic: ' + $json.topic + ', zamówienie: ' + $json.zamowienie }}", "string")])
c3, f3 = append_csv(wf1, "Log błędów (podpis)", 1200, 480, "log_bledow.csv")
r_401 = respond(wf1, "Odpowiedź: 401", 1640, 480, 401, "={{ { ok: false, blad: 'nieprawidłowy podpis webhooka' } }}")

wf1.chain(w, v, ping)
wf1.link(ping, r_ping, 0)
wf1.link(ping, sig, 1)
wf1.link(sig, dane, 0)
wf1.link(sig, bad_row, 1)
wf1.link(dane, row, 0)
wf1.link(dane, err_row, 1)
wf1.link(row, c1)
# Odpowiedź do WooCommerce zaraz po zapisie (WooCommerce czeka na nią przy tworzeniu zamówienia),
# e-mail i Discord wykonują się już po odpowiedzi.
wf1.chain(f1, r_ok, mail_ok, d_ok)
wf1.link(err_row, c2)
wf1.chain(f2, r_422, mail_err, d_err)
wf1.link(bad_row, c3)
wf1.chain(f3, r_401)
wf1.dump("WF1_zamowienie.json")

# ------------------------------------------------------------------------------------- WF2
LOW = r"""// Produkty z włączonym stanem magazynowym i stanem ≤ progu.
const cfg = $('Konfiguracja').first().json;
const all = $input.all().map(i => i.json);
const low = all
  .filter(p => p.manage_stock && Number(p.stock_quantity) <= cfg.prog)
  .sort((a, b) => a.stock_quantity - b.stock_quantity)
  .map(p => ({ nazwa: p.name, sku: p.sku, stan: Number(p.stock_quantity) }));
const rows = low.map(p => `<tr><td>${p.nazwa}</td><td>${p.sku}</td><td align="right"><b>${p.stan}</b></td></tr>`).join('');
return [{ json: {
  sprawdzono: all.length, prog: cfg.prog, liczba: low.length, produkty: low,
  tekst: low.map(p => `• ${p.nazwa} (${p.sku}): ${p.stan} szt.`).join('\n'),
  html: `<p>Kontrola z ${$now.toFormat('dd.LL.yyyy HH:mm')}: ${low.length} z ${all.length} produktów ma stan ≤ ${cfg.prog} szt.</p>` +
        `<table border="1" cellpadding="6" style="border-collapse:collapse"><tr><th>Produkt</th><th>SKU</th><th>Stan</th></tr>${rows}</table>`,
} }];"""

L = "$('Niskie stany').first().json"
wf2 = WF("KNKstanyMagazyn1", "WF2 – Kontrola stanów magazynowych (cron)", error_wf="KNKobslugaBledow")
cron = wf2.node("Codziennie 07:00", "scheduleTrigger", 1.2, 0, 100,
                {"rule": {"interval": [{"field": "cronExpression", "expression": "0 7 * * *"}]}})
hook = wf2.node("Uruchom na żądanie (GET)", "webhook", 2, 0, 300,
                {"httpMethod": "GET", "path": "kontrola-stanow", "responseMode": "onReceived", "options": {}},
                webhookId="knk-kontrola-stanow")
cfg = set_node(wf2, "Konfiguracja", 240, 200, [
    ("prog", "5", "number"), ("api", "https://kawanaklik.local/wp-json/wc/v3/products", "string"),
    ("magazyn", "magazyn@kawanaklik.test", "string")])
api = wf2.node("API WooCommerce: produkty", "httpRequest", 4.2, 480, 200, {
    "url": "={{ $json.api }}", "authentication": "predefinedCredentialType", "nodeCredentialType": "wooCommerceApi",
    "sendQuery": True, "queryParameters": {"parameters": [{"name": "per_page", "value": "100"},
                                                          {"name": "status", "value": "publish"}]},
    "options": {"allowUnauthorizedCerts": True, "timeout": 10000}},
    credentials=WOO, retryOnFail=True, maxTries=3, waitBetweenTries=3000, onError="continueErrorOutput")
low = wf2.node("Niskie stany", "code", 2, 720, 100, {"jsCode": LOW})
anylow = if_node(wf2, "Są niskie stany?", 960, 100, "={{ $json.liczba }}", "gt", 0, typ="number")
mail_low = email(wf2, "E-mail: raport do magazynu", 1200, 0, f"={{{{ $('Konfiguracja').first().json.magazyn }}}}",
                 f"=📦 Niskie stany magazynowe: {{{{ {L}.liczba }}}} produkty",
                 f"={{{{ {L}.html }}}}<p>Zamów towar u dostawcy. Raport wysłał automat n8n.</p>")
d_low = discord(wf2, "Discord: alert stanów", 1420, 0,
                f"`📦 Niskie stany (≤ ${{{L}.prog}} szt.):\\n${{{L}.tekst}}`")
log_row = set_node(wf2, "Wiersz logu kontroli", 1660, 160, [
    ("czas", NOW, "string"), ("sprawdzono", f"={{{{ {L}.sprawdzono }}}}", "number"),
    ("niskie", f"={{{{ {L}.liczba }}}}", "number"),
    ("produkty", f"={{{{ {L}.produkty.map(p => p.sku + '=' + p.stan).join(', ') || 'wszystko OK' }}}}", "string")])
c4, f4 = append_csv(wf2, "Log kontroli", 1880, 160, "log_kontroli_stanow.csv")
# Awaria API
down_row = set_node(wf2, "Wiersz logu: awaria API", 720, 380, [
    ("czas", NOW, "string"), ("zrodlo", "WF2 – API WooCommerce", "string"),
    ("opis", "API WooCommerce nie odpowiada (3 próby, co 3 s)", "string"),
    ("szczegoly", "={{ $json.error?.message || $json.message || JSON.stringify($json).slice(0, 200) }}", "string")])
c5, f5 = append_csv(wf2, "Log błędów (API)", 960, 380, "log_bledow.csv")
d_down = discord(wf2, "Discord: awaria API", 1400, 380,
                 "`🔴 Kontrola stanów nie powiodła się – API WooCommerce nie odpowiada. Sprawdź serwer sklepu.`")
mail_down = email(wf2, "E-mail: awaria do kierownika", 1620, 380, "kierownik@kawanaklik.test",
                  "=🔴 Awaria API WooCommerce – kontrola stanów nie wykonana",
                  f"=<p>Automat n8n nie mógł pobrać produktów z API sklepu ({{{{ $now.toFormat('dd.LL.yyyy HH:mm') }}}}).</p>"
                  f"<p>Szczegóły: {{{{ $('Wiersz logu: awaria API').first().json.szczegoly }}}}</p>"
                  f"<p>Kontrola zostanie powtórzona jutro o 07:00 – można ją też uruchomić ręcznie.</p>")
wf2.link(cron, cfg)
wf2.link(hook, cfg)
wf2.link(cfg, api)
wf2.link(api, low, 0)
wf2.link(api, down_row, 1)
wf2.link(low, anylow)
wf2.link(anylow, mail_low, 0)
wf2.link(anylow, log_row, 1)
wf2.chain(mail_low, d_low, log_row, c4)
wf2.link(down_row, c5)
wf2.chain(f5, d_down, mail_down)
wf2.dump("WF2_kontrola_stanow.json")

# ------------------------------------------------------------------------------------- WF3
wf3 = WF("KNKobslugaBledow", "WF3 – Obsługa błędów (Error Trigger)")
t = wf3.node("Błąd w przepływie", "errorTrigger", 1, 0, 100, {})
row = set_node(wf3, "Wiersz logu błędu", 240, 100, [
    ("czas", NOW, "string"), ("zrodlo", "={{ $json.workflow.name }}", "string"),
    ("opis", "={{ $json.execution.error.message }}", "string"),
    ("szczegoly", "={{ 'węzeł: ' + ($json.execution.lastNodeExecuted || '-') + ', wykonanie #' + ($json.execution.id || '-') }}",
     "string")])
c6, f6 = append_csv(wf3, "Log błędów", 480, 100, "log_bledow.csv")
d3 = discord(wf3, "Discord: błąd przepływu", 920, 100,
             "`🛑 Błąd w przepływie „${$('Wiersz logu błędu').first().json.zrodlo}”: ${$('Wiersz logu błędu').first().json.opis}`")
m3 = email(wf3, "E-mail: błąd do administratora", 1140, 100, "admin@kawanaklik.test",
           "=🛑 Błąd przepływu n8n: {{ $('Wiersz logu błędu').first().json.zrodlo }}",
           "=<p><b>{{ $('Wiersz logu błędu').first().json.opis }}</b></p><p>{{ $('Wiersz logu błędu').first().json.szczegoly }}</p>"
           "<p>Czas: {{ $('Wiersz logu błędu').first().json.czas }}</p>")
wf3.chain(t, row, c6)
wf3.chain(f6, d3, m3)
wf3.dump("WF3_obsluga_bledow.json")

print("OK:", [p.name for p in sorted(OUT.glob("WF*.json"))])
