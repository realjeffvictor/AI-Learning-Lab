#!/usr/bin/env bash
# Checks a deployed site. Usage: scripts/smoke_prod.sh https://your-site.example [https://your-api.example]
# The second argument (the API's own address) additionally checks that API docs are hidden.
set -uo pipefail
BASE="${1:-}"
[ -n "$BASE" ] || { echo "Usage: $0 https://your-site.example [https://your-api.example]"; exit 2; }
BASE="${BASE%/}"
fail=0
report() { if [ "$2" = "ok" ]; then echo "PASS  $1"; else echo "FAIL  $1  ($3)"; fail=1; fi; }

HEADERS="$(curl -s -m 90 -D - -o /tmp/ail_smoke_body "$BASE/api/v1/health" || true)"
CODE="$(printf '%s' "$HEADERS" | head -1 | awk '{print $2}')"
[ "$CODE" = "200" ] && report "health answers 200" ok || report "health answers 200" bad "got ${CODE:-nothing}; a sleeping free instance can need a minute, retry"
grep -q '"database":"ok"' /tmp/ail_smoke_body 2>/dev/null && report "database reachable" ok || report "database reachable" bad "health body lacks database ok"
printf '%s' "$HEADERS" | grep -qi '^x-content-type-options: nosniff' && report "nosniff header" ok || report "nosniff header" bad "missing"
printf '%s' "$HEADERS" | grep -qi '^strict-transport-security:' && report "HSTS header" ok || report "HSTS header" bad "missing (expected on https production)"

STATUS="$(curl -s -m 60 -o /dev/null -w '%{http_code}' "$BASE/api/v1/courses" || true)"
[ "$STATUS" = "401" ] && report "protected route needs a token" ok || report "protected route needs a token" bad "got $STATUS"
STATUS="$(curl -s -m 60 -o /dev/null -w '%{http_code}' "$BASE/api/v1/certificates/verify/does-not-exist" || true)"
[ "$STATUS" = "404" ] && report "unknown certificate is 404" ok || report "unknown certificate is 404" bad "got $STATUS"
if [ -n "${2:-}" ]; then
  STATUS="$(curl -s -m 60 -o /dev/null -w '%{http_code}' "${2%/}/docs" || true)"
  [ "$STATUS" = "404" ] && report "API docs hidden in production" ok || report "API docs hidden in production" bad "got $STATUS"
fi
rm -f /tmp/ail_smoke_body
exit "$fail"
