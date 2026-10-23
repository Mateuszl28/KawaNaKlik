#!/bin/bash
# Testy przepływów n8n KawaNaKlik (APPDB Etap II). Uruchamiać z katalogu głównego projektu
# (tam, gdzie leży dane_testowe/ – klucze testowe nie są w repozytorium).
#   bash APPDB_LAB03/kod/testy/testy_n8n.sh > APPDB_LAB03/testy/wyniki_testow.txt
T="$(cd "$(dirname "$0")" && pwd)"
N8N=http://localhost:5690
PLIKI="C:/Users/lagoc/.n8n-kawanaklik/pliki"
MAILPIT=http://localhost:10007
export PYTHONIOENCODING=utf-8

naglowek() { echo; echo "=================== $1"; echo "czas: $(date '+%Y-%m-%d %H:%M:%S')"; }
csv() { echo "--- $1.csv (ostatnie $2):"; tail -n "$2" "$PLIKI/$1.csv"; }
maile() {
  echo "--- Mailpit (ostatnie $1):"
  curl -s "$MAILPIT/api/v1/messages?limit=$1" | python -c "import json,sys
for m in json.load(sys.stdin)['messages']: print(' ', m['Created'][11:19], m['To'][0]['Address'], '|', m['Subject'])"
}
zamowienie() { python "$T/wc.py" POST orders "$1" | python -c "import json,sys
o=json.load(sys.stdin); print('WooCommerce: utworzono zamówienie', o.get('number'), 'kwota', o.get('total'))"; }

naglowek "T7 – awaria API: zatrzymana strona sklepu (Local) → 3 próby → log + alert"
# T7 idzie pierwszy: Local zatrzymuje razem ze stroną Mailpit, który po restarcie traci zapisane wiadomości.
python "$T/local_site.py" stop
curl -s -w "  [HTTP %{http_code}]\n" $N8N/webhook/kontrola-stanow
sleep 30; csv log_bledow 1; csv discord_mock 1
python "$T/local_site.py" start
for i in $(seq 1 30); do curl -sk -o /dev/null -w "%{http_code}" https://kawanaklik.local/ | grep -q 200 && break; sleep 2; done
echo "sklep znowu odpowiada"

naglowek "T1 – poprawne zamówienie (WooCommerce → webhook → arkusz → e-mail → Discord)"
zamowienie '{"payment_method":"bacs","payment_method_title":"Przelew bankowy","status":"processing",
 "billing":{"first_name":"Anna","last_name":"Testowa","address_1":"ul. Kawowa 12","city":"Kraków","postcode":"30-001",
 "country":"PL","email":"anna.testowa@example.com","phone":"+48 500 100 200"},
 "line_items":[{"product_id":13,"quantity":2},{"product_id":21,"quantity":1}],"customer_note":"T1"}'
sleep 4; csv arkusz_zamowien 1; csv discord_mock 1; maile 3

naglowek "T2 – zamówienie bez e-maila i adresu (dane niekompletne)"
zamowienie '{"payment_method":"cod","payment_method_title":"Płatność przy odbiorze","status":"processing",
 "billing":{"first_name":"Ewa","last_name":"Niepełna","phone":"+48 511 222 333","country":"PL"},
 "line_items":[{"product_id":17,"quantity":1}],"customer_note":"T2"}'
sleep 4; csv log_bledow 1; csv discord_mock 1; maile 1

naglowek "T2b – niepoprawny adres e-mail (podpisany webhook wysłany bezpośrednio)"
python "$T/signed_post.py" "$T/zamowienie_zly_email.json"
sleep 2; csv log_bledow 1

naglowek "T3 – fałszywy podpis HMAC"
curl -s -w "  [HTTP %{http_code}]\n" -X POST $N8N/webhook/zamowienie -H 'Content-Type: application/json' \
  -H 'X-WC-Webhook-Topic: order.created' -H 'X-WC-Webhook-Signature: ZmFsc3l3eS1wb2RwaXM=' \
  -d '{"id":999,"number":"999","billing":{"email":"atak@example.com"}}'
naglowek "T3b – brak podpisu"
curl -s -w "  [HTTP %{http_code}]\n" -X POST $N8N/webhook/zamowienie -H 'Content-Type: application/json' -d '{"id":998}'
sleep 2; csv log_bledow 2

naglowek "T4 – ping WooCommerce przy zapisie webhooka"
curl -s -w "  [HTTP %{http_code}]\n" -X POST $N8N/webhook/zamowienie -H 'Content-Type: application/x-www-form-urlencoded' -d 'webhook_id=1'

naglowek "T5 – nieobsłużony wyjątek w WF1 (notatka #TEST-BLAD) → WF3 Error Trigger"
zamowienie '{"payment_method":"bacs","payment_method_title":"Przelew bankowy","status":"processing",
 "billing":{"first_name":"Tomasz","last_name":"Błędny","address_1":"ul. Liberica 7","city":"Łódź","postcode":"90-001",
 "country":"PL","email":"tomasz.bledny@example.com","phone":"+48 522 333 444"},
 "line_items":[{"product_id":15,"quantity":1}],"customer_note":"#TEST-BLAD"}'
sleep 6; csv log_bledow 1; csv discord_mock 1; maile 1

naglowek "T6 – kontrola stanów magazynowych (to samo co cron 07:00, uruchomione przez GET)"
curl -s -w "  [HTTP %{http_code}]\n" $N8N/webhook/kontrola-stanow
sleep 6; csv log_kontroli_stanow 1; csv discord_mock 5; maile 1

naglowek "Podsumowanie wykonań w n8n"
J=$(mktemp); PW=$(sed -n 's/^haslo: //p' dane_testowe/n8n_owner_test.txt)
curl -s -c "$J" -X POST $N8N/rest/login -H 'Content-Type: application/json' \
  -d "{\"emailOrLdapLoginId\":\"admin@kawanaklik.test\",\"password\":\"$PW\"}" -o /dev/null
curl -s -b "$J" "$N8N/rest/executions?limit=20" | python -c "import json,sys
for e in json.load(sys.stdin)['data']['results']: print(' #%s %-17s %-8s %s' % (e['id'], e['workflowId'], e['status'], e['startedAt'][11:19]))"
rm -f "$J"
