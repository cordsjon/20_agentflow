#!/usr/bin/env bash
# WhatsApp message sender via Twilio API
# Usage: send.sh <recipient_number> <message>
# Requires: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM

set -euo pipefail

RECIPIENT="$1"
MESSAGE="$2"

# Validate env vars
for var in TWILIO_ACCOUNT_SID TWILIO_AUTH_TOKEN TWILIO_WHATSAPP_FROM; do
  if [ -z "${!var:-}" ]; then
    echo "ERROR: $var is not set" >&2
    exit 1
  fi
done

# Validate inputs
if [ -z "$RECIPIENT" ]; then
  echo "ERROR: No recipient number provided" >&2
  exit 1
fi

if [ -z "$MESSAGE" ]; then
  echo "ERROR: No message provided" >&2
  exit 1
fi

# Ensure recipient has whatsapp: prefix for Twilio
TO="whatsapp:${RECIPIENT}"

# Send via Twilio REST API
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_ACCOUNT_SID}/Messages.json" \
  -u "${TWILIO_ACCOUNT_SID}:${TWILIO_AUTH_TOKEN}" \
  --data-urlencode "From=${TWILIO_WHATSAPP_FROM}" \
  --data-urlencode "To=${TO}" \
  --data-urlencode "Body=${MESSAGE}")

# Split response body and HTTP status code
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  SID=$(echo "$BODY" | grep -o '"sid":"[^"]*"' | head -1 | cut -d'"' -f4)
  echo "OK|${SID}|${RECIPIENT}"
else
  ERROR_CODE=$(echo "$BODY" | grep -o '"code":[0-9]*' | head -1 | cut -d':' -f2)
  ERROR_MSG=$(echo "$BODY" | grep -o '"message":"[^"]*"' | head -1 | cut -d'"' -f4)
  echo "FAIL|${ERROR_CODE}|${ERROR_MSG}" >&2
  exit 1
fi
