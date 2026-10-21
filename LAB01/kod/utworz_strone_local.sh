#!/bin/bash
# Tworzy stronę WordPress "KawaNaKlik" w aplikacji Local przez jej lokalne API GraphQL
# (to samo, co kliknięcie "+ Add site" w Local). Hasło admina podaj w zmiennej WP_PASS.
#   WP_PASS='...' ./utworz_strone_local.sh
set -e
INFO="$APPDATA/Local/graphql-connection-info.json"
TOKEN=$(node -e "console.log(require(process.argv[1]).authToken)" "$INFO")

BODY=$(node -e '
console.log(JSON.stringify({
  query: "mutation($i: AddSiteInput!) { addSite(input: $i) { id status } }",
  variables: { i: {
    name: "KawaNaKlik",
    path: "~/Local Sites/kawanaklik",
    domain: "kawanaklik.local",
    wpAdminUsername: "admin",
    wpAdminPassword: process.env.WP_PASS,
    wpAdminEmail: "admin@kawanaklik.local",
    goToSite: true
  } }
}))')

curl -s -X POST http://127.0.0.1:4000/graphql \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "$BODY"
