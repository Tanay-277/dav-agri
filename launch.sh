#!/usr/bin/env bash
# ==============================================================================
# DAV Production Launch Script (bash)
# ==============================================================================
# Usage: ./launch.sh
# Builds and starts the production Docker stack, waits for health checks,
# and prints access URLs.
# ==============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log()  { printf "${CYAN}==>${NC} %s\n" "$*"; }
ok()   { printf "${GREEN}[OK]${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}[WARN]${NC} %s\n" "$*"; }
err()  { printf "${RED}[ERROR]${NC} %s\n" "$*"; }

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

# ---------------------------------------------------------------------------
# 1. Check Docker is running
# ---------------------------------------------------------------------------
log "Checking Docker..."
if ! docker info >/dev/null 2>&1; then
    err "Docker is not running. Start Docker Desktop and try again."
    exit 1
fi
ok "Docker is running."

# ---------------------------------------------------------------------------
# 2. Verify .env.production exists and has been edited (not placeholders)
# ---------------------------------------------------------------------------
if [ ! -f "$ENV_FILE" ]; then
    err "$ENV_FILE not found. Copy .env.example to .env.production and fill in real values."
    exit 1
fi

# Placeholder patterns that indicate the file has not been edited.
PLACEHOLDER_PATTERNS=(
    "replace_with_secure_random_32_byte_key"
    "replace_with_secure_db_password"
    "replace_with_secure_random_jwt_secret"
    "replace_with_twilio_account_sid"
    "replace_with_twilio_auth_token"
    "replace_with_twilio_from_number"
    "replace_with_google_client_id"
    "replace_with_google_client_secret"
    "replace_with_gemini_api_key"
    "your-domain.com"
)

FOUND_PLACEHOLDERS=0
for pattern in "${PLACEHOLDER_PATTERNS[@]}"; do
    if grep -Eq "$pattern" "$ENV_FILE"; then
        warn "Placeholder found in $ENV_FILE: '$pattern'"
        FOUND_PLACEHOLDERS=$((FOUND_PLACEHOLDERS + 1))
    fi
done

if [ "$FOUND_PLACEHOLDERS" -gt 0 ]; then
    err "$ENV_FILE contains $FOUND_PLACEHOLDERS placeholder value(s). Edit it before deploying."
    exit 1
fi
ok "$ENV_FILE exists and has no placeholder values."

# ---------------------------------------------------------------------------
# 3. Build and start the production stack
# ---------------------------------------------------------------------------
log "Stopping any existing production containers..."
docker compose -f "$COMPOSE_FILE" down --remove-orphans >/dev/null 2>&1 || true

log "Building and starting production stack (this may take a few minutes)..."
docker compose -f "$COMPOSE_FILE" up -d --build

ok "Stack started. Waiting for health checks..."

# ---------------------------------------------------------------------------
# 4. Wait for health checks
# ---------------------------------------------------------------------------
MAX_WAIT=120
ELAPSED=0
INTERVAL=5

while [ "$ELAPSED" -lt "$MAX_WAIT" ]; do
    HEALTHY=$(docker compose -f "$COMPOSE_FILE" ps --format '{{.Service}} {{.Status}}' 2>/dev/null | grep -ci "healthy" || true)
    TOTAL=$(docker compose -f "$COMPOSE_FILE" ps --format '{{.Service}}' 2>/dev/null | wc -l | tr -d ' ')

    if [ "${HEALTHY:-0}" -gt 0 ] && [ "${HEALTHY:-0}" -eq "${TOTAL:-0}" ]; then
        ok "All $TOTAL services healthy after ${ELAPSED}s."
        break
    fi

    sleep "$INTERVAL"
    ELAPSED=$((ELAPSED + INTERVAL))
    log "Waiting... (${ELAPSED}s / ${MAX_WAIT}s) - ${HEALTHY:-0}/${TOTAL:-0} healthy"
done

if [ "$ELAPSED" -ge "$MAX_WAIT" ]; then
    err "Health checks did not complete within ${MAX_WAIT}s."
    docker compose -f "$COMPOSE_FILE" ps
    exit 1
fi

# ---------------------------------------------------------------------------
# 5. Print access URLs and status
# ---------------------------------------------------------------------------
echo
echo "============================================="
echo "     DAV Production Stack - RUNNING"
echo "============================================="
echo
docker compose -f "$COMPOSE_FILE" ps
echo
echo "Access URLs:"
echo "  Frontend (web app):   http://localhost"
echo "  Backend API:          http://localhost:8101"
echo "  Backend API docs:     http://localhost:8101/docs"
echo "  Health check:         http://localhost:8101/health"
echo
echo "Container management:"
echo "  Stop:    docker compose -f $COMPOSE_FILE down"
echo "  Logs:    docker compose -f $COMPOSE_FILE logs -f"
echo "  Restart: docker compose -f $COMPOSE_FILE restart"
echo
