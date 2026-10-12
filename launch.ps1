<#
.SYNOPSIS
    DAV Production Launch Script (PowerShell)
.DESCRIPTION
    Builds and starts the production Docker stack, waits for health checks,
    and prints access URLs.
.NOTES
    Usage: .\launch.ps1
#>

$ErrorActionPreference = "Stop"

$RED    = "Red"
$GREEN  = "Green"
$YELLOW = "Yellow"
$CYAN   = "Cyan"

function log  { Write-Host "==>" -ForegroundColor $CYAN -NoNewline; Write-Host " $args" }
function ok   { Write-Host "[OK]" -ForegroundColor $GREEN  -NoNewline;   Write-Host " $args" }
function warn { Write-Host "[WARN]" -ForegroundColor $YELLOW -NoNewline; Write-Host " $args" }
function err  { Write-Host "[ERROR]" -ForegroundColor $RED    -NoNewline; Write-Host " $args" }

$PROJECT_DIR = $PSScriptRoot
Set-Location -LiteralPath $PROJECT_DIR

$COMPOSE_FILE = "docker-compose.prod.yml"
$ENV_FILE     = ".env.production"

# ---------------------------------------------------------------------------
# 1. Check Docker is running
# ---------------------------------------------------------------------------
log "Checking Docker..."
try {
    $null = docker info 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
} catch {
    err "Docker is not running. Start Docker Desktop and try again."
    exit 1
}
ok "Docker is running."

# ---------------------------------------------------------------------------
# 2. Verify .env.production exists and has been edited (not placeholders)
# ---------------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $ENV_FILE)) {
    err "$ENV_FILE not found. Copy .env.example to .env.production and fill in real values."
    exit 1
}

$PLACEHOLDER_PATTERNS = @(
    "replace_with_secure_random_32_byte_key",
    "replace_with_secure_db_password",
    "replace_with_secure_random_jwt_secret",
    "replace_with_twilio_account_sid",
    "replace_with_twilio_auth_token",
    "replace_with_twilio_from_number",
    "replace_with_google_client_id",
    "replace_with_google_client_secret",
    "replace_with_gemini_api_key",
    "your-domain.com"
)

$FOUND_PLACEHOLDERS = 0
$ENV_CONTENT = Get-Content -Raw -LiteralPath $ENV_FILE
foreach ($pattern in $PLACEHOLDER_PATTERNS) {
    if ($ENV_CONTENT -match [regex]::Escape($pattern)) {
        warn "Placeholder found in $ENV_FILE : '" + $pattern + "'"
        $FOUND_PLACEHOLDERS++
    }
}

if ($FOUND_PLACEHOLDERS -gt 0) {
    err "$ENV_FILE contains $FOUND_PLACEHOLDERS placeholder value(s). Edit it before deploying."
    exit 1
}
ok "$ENV_FILE exists and has no placeholder values."

# ---------------------------------------------------------------------------
# 3. Build and start the production stack
# ---------------------------------------------------------------------------
log "Stopping any existing production containers..."
docker compose -f $COMPOSE_FILE down --remove-orphans 2>$null

log "Building and starting production stack (this may take a few minutes)..."
docker compose -f $COMPOSE_FILE up -d --build
if ($LASTEXITCODE -ne 0) { err "docker compose up failed."; exit 1 }

ok "Stack started. Waiting for health checks..."

# ---------------------------------------------------------------------------
# 4. Wait for health checks
# ---------------------------------------------------------------------------
$MAX_WAIT = 120
$ELAPSED  = 0
$INTERVAL = 5

while ($ELAPSED -lt $MAX_WAIT) {
    $psOutput = docker compose -f $COMPOSE_FILE ps --format "{{.Service}} {{.Status}}" 2>$null
    $HEALTHY = ($psOutput -match "healthy").Count
    $TOTAL   = ($psOutput -match "^(backend|frontend|postgres)").Count

    if ($HEALTHY -gt 0 -and $HEALTHY -eq $TOTAL -and $TOTAL -gt 0) {
        ok "All $TOTAL services healthy after ${ELAPSED}s."
        break
    }

    Start-Sleep -Seconds $INTERVAL
    $ELAPSED += $INTERVAL
    log "Waiting... (${ELAPSED}s / ${MAX_WAIT}s) - ${HEALTHY}/${TOTAL} healthy"
}

if ($ELAPSED -ge $MAX_WAIT) {
    err "Health checks did not complete within ${MAX_WAIT}s."
    docker compose -f $COMPOSE_FILE ps
    exit 1
}

# ---------------------------------------------------------------------------
# 5. Print access URLs and status
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "=============================================" -ForegroundColor $YELLOW
Write-Host "     DAV Production Stack - RUNNING" -ForegroundColor $YELLOW
Write-Host "=============================================" -ForegroundColor $YELLOW
Write-Host ""

docker compose -f $COMPOSE_FILE ps

Write-Host ""
Write-Host "Access URLs:"
Write-Host "  Frontend (web app):   http://localhost"
Write-Host "  Backend API:          http://localhost:8101"
Write-Host "  Backend API docs:     http://localhost:8101/docs"
Write-Host "  Health check:         http://localhost:8101/health"
Write-Host ""
Write-Host "Container management:"
Write-Host "  Stop:    docker compose -f $COMPOSE_FILE down"
Write-Host "  Logs:    docker compose -f $COMPOSE_FILE logs -f"
Write-Host "  Restart: docker compose -f $COMPOSE_FILE restart"
Write-Host ""
