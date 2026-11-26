#!/usr/bin/env bash
# Writes frontend/vercel.json. Usage: scripts/make_vercel_json.sh https://your-api.onrender.com
# /api/* is proxied to the API so the browser only ever talks to one origin (first-party cookies, no CORS).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API="${1:-}"
[[ "$API" =~ ^https://[A-Za-z0-9.-]+(:[0-9]+)?$ ]] || { echo "Usage: $0 https://your-api-host   (https, no trailing slash, no path)"; exit 2; }
OUT="$ROOT/frontend/vercel.json"
cat > "$OUT" <<JSON
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "${API}/api/:path*" },
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Referrer-Policy", "value": "no-referrer" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" },
        { "key": "Content-Security-Policy-Report-Only", "value": "default-src 'self'; script-src 'self' 'wasm-unsafe-eval' https://cdn.jsdelivr.net; worker-src 'self' blob:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' data: https://cdn.jsdelivr.net; img-src 'self' data:; connect-src 'self' https://cdn.jsdelivr.net; frame-ancestors 'none'; base-uri 'self'; form-action 'self'" }
      ]
    }
  ]
}
JSON
python3 -m json.tool "$OUT" >/dev/null
echo "Wrote $OUT. Commit it, then deploy. The CSP is report-only until you have checked the browser console (see docs/DEPLOYMENT.md)."
