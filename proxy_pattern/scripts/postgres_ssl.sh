#!/usr/bin/env bash
# Generate self-signed SSL/TLS certificates for the PostgreSQL container.
# Certificates are written to proxy_pattern/certs/ and can be bind-mounted
# into the postgres container to enable server-side SSL.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
CERTS_DIR="$BASE_DIR/certs"
CERT="$CERTS_DIR/server.crt"
KEY="$CERTS_DIR/server.key"
DAYS=365
SUBJ="/CN=postgres/O=LiteLLM/C=US"

# ── Prerequisites ─────────────────────────────────────────────────────────────

if ! command -v openssl >/dev/null 2>&1; then
    echo "Error: openssl is required but not installed." >&2
    echo "  macOS:  brew install openssl" >&2
    echo "  Debian: sudo apt-get install openssl" >&2
    exit 1
fi

# ── Guard against accidental overwrite ────────────────────────────────────────

if [ -f "$CERT" ] || [ -f "$KEY" ]; then
    echo "Warning: certificates already exist in $CERTS_DIR/"
    printf "Overwrite? (y/N): "
    read -r REPLY
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Existing certificates preserved."
        exit 0
    fi
fi

mkdir -p "$CERTS_DIR"

# ── Generate ──────────────────────────────────────────────────────────────────

echo "Generating self-signed certificate (${DAYS} days) ..."

openssl req \
    -new -x509 \
    -days "$DAYS" \
    -nodes \
    -subj "$SUBJ" \
    -out "$CERT" \
    -keyout "$KEY" \
    2>/dev/null

# PostgreSQL refuses to start if the private key is group- or world-readable.
chmod 600 "$KEY"
chmod 644 "$CERT"

echo ""
echo "Done."
echo ""
echo "  $CERT"
echo "  $KEY"
echo ""

# ── Show certificate details ──────────────────────────────────────────────────

openssl x509 -noout -subject -dates -fingerprint -in "$CERT"
echo ""

# ── docker-compose integration instructions ───────────────────────────────────

cat <<'EOF'
─── docker-compose.yml integration ─────────────────────────────────────────────

Add to the postgres service volumes:
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./certs/server.crt:/etc/ssl/postgres/server.crt:ro
    - ./certs/server.key:/etc/ssl/postgres/server.key:ro

Replace the ssl=off command override with:
  command: >
    postgres
    -c ssl=on
    -c ssl_cert_file=/etc/ssl/postgres/server.crt
    -c ssl_key_file=/etc/ssl/postgres/server.key

NOTE: PostgreSQL rejects key files that are readable by other users (mode > 0600).
When bind-mounting, the file is owned by your host user.  The postgres:16-alpine
container runs as uid 70; it cannot read a key owned by a different uid.
Two options:

  Option A (simplest) — remove 'user: postgres' from the postgres service so
  the process runs as root inside the container and can read uid-0 key files.

  Option B — set ownership on the host to match the container uid:
    sudo chown 70:70 certs/server.key

─────────────────────────────────────────────────────────────────────────────────
EOF
