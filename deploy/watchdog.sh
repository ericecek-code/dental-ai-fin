#!/usr/bin/env bash
# ===============================================================
# DenteScope AI — Production watchdog
# Monitoruje endpoint a reštartuje lokálny RunPod Pod pri výpadku.
#
# Pouzitie:
#   1) Nastav RUNPOD_API_KEY, RUNPOD_POD_ID, RUNPOD_HEALTH_URL v .env
#   2) Spust ako cron job kazdych 5 minut:
#        */5 * * * * /c/Users/PC1/Desktop/dental-ai/deploy/watchdog.sh
#
# Alebo ako Windows Scheduled Task.
# Alternativne toto vie spustat Hermes pravidelne (ja to viem nastavit).
# ===============================================================

set -euo pipefail

# Nacitaj .env ak existuje
ENV_FILE="$(dirname "$0")/../.env"
if [ -f "$ENV_FILE" ]; then
  set -a; . "$ENV_FILE"; set +a
fi

# Fallback - ak env nie je, ukonci
: "${RUNPOD_API_KEY:=}"
: "${RUNPOD_POD_ID:=}"
: "${RUNPOD_HEALTH_URL:=}"

if [ -z "$RUNPOD_HEALTH_URL" ]; then
  echo "[$(date -Iseconds)] ERROR: RUNPOD_HEALTH_URL nie je nastavene" >&2
  exit 2
fi

# Health check (timeout 4s, fail-fest)
if curl -sf -m 4 "$RUNPOD_HEALTH_URL/health" -o /dev/null; then
  # OK - nic neurob
  echo "[$(date -Iseconds)] OK - backend bezi"
  exit 0
fi

echo "[$(date -Iseconds)] FAIL - backend neodpoveda na $RUNPOD_HEALTH_URL"

# Ak mame pod ID + API token, restart
if [ -n "$RUNPOD_API_KEY" ] && [ -n "$RUNPOD_POD_ID" ]; then
  echo "[$(date -Iseconds)] Reštartujem pod $RUNPOD_POD_ID cez RunPod API..."

  curl -sf -X POST "https://api.runpod.io/v2/pod/$RUNPOD_POD_ID/restart" \
    -H "Authorization: Bearer $RUNPOD_API_KEY" \
    -o /dev/null \
    || echo "[$(date -Iseconds)] Restart zlyhal, skontroluj API token" >&2
else
  echo "[$(date -Iseconds)] Nemam RUNPOD_API_KEY/POD_ID, manual check potrebny"
fi

exit 1
