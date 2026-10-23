#!/bin/bash
# Start lokalnego n8n dla laboratorium APPDB (KawaNaKlik).
# Dane n8n (baza SQLite, poświadczenia) trzymamy poza repozytorium.
export N8N_USER_FOLDER="C:/Users/lagoc/.n8n-kawanaklik"
export N8N_PORT=5690                               # 5678 zajmuje inna instancja n8n
export N8N_RUNNERS_BROKER_PORT=5691                # broker task-runnera (domyślny 5679 też zajęty)
export N8N_SECURE_COOKIE=false                      # http://localhost (bez HTTPS) – tylko lokalnie
export N8N_RESTRICT_FILE_ACCESS_TO="C:/Users/lagoc/.n8n-kawanaklik/pliki"
export NODE_FUNCTION_ALLOW_BUILTIN=crypto           # Code node: weryfikacja HMAC webhooka
export N8N_BLOCK_ENV_ACCESS_IN_NODE=false           # $env.WC_WEBHOOK_SECRET, $env.DISCORD_WEBHOOK_URL
export GENERIC_TIMEZONE="Europe/Warsaw"
export N8N_DIAGNOSTICS_ENABLED=false
export N8N_VERSION_NOTIFICATIONS_ENABLED=false
export WC_WEBHOOK_SECRET="$(cat "$N8N_USER_FOLDER/wc_webhook_secret.txt")"
# export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."   # prawdziwy kanał; domyślnie mock WF0
# N8N_BIN – ścieżka do zainstalowanego n8n (npm/pnpm install n8n); domyślnie istniejąca instalacja pnpm
N8N_BIN="${N8N_BIN:-C:/Users/lagoc/n8n-pnpm/node_modules/n8n/bin/n8n}"
exec node "$N8N_BIN" start
