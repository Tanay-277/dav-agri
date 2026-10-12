<#
.SYNOPSIS
    Exposes the DAV stack to a real phone over a trusted HTTPS URL.

.DESCRIPTION
    DAV is voice-first, so the browser microphone must work. Browsers only grant
    getUserMedia in a "secure context", and a plain http:// LAN address is not one.
    A self-signed certificate does not reliably satisfy phone browsers either: an
    untrusted origin is still treated as insecure, and the user must accept a
    warning first.

    A Cloudflare quick tunnel solves this without touching the router or the
    firewall. The phone sees a real public hostname with a Google Trust Services
    certificate, so the origin is trusted and getUserMedia is granted with no
    warning. Traffic is encrypted end to end: the phone terminates TLS with
    Cloudflare's edge, cloudflared forwards to the local nginx, and the phone
    never sees the self-signed development certificate.

    The quick tunnel assigns a NEW random hostname on every restart, so the
    Google OAuth authorized-JavaScript-origin must be updated to match. Print
    the origin printed here and add it in the Google Cloud console without a
    trailing slash.

.PARAMETER Origin
    Serve plain HTTP on :8080 instead of HTTPS. Useful for UI-only work; the
    microphone will be blocked on a real handset.

.PARAMETER PrintOnly
    Print the cloudflared command to run and exit, without starting anything.

.EXAMPLE
    ./start-tunnel.ps1
    Prints: https://<random>.trycloudflare.com   -> open this on the phone

.EXAMPLE
    ./start-tunnel.ps1 -Origin
    Tunnels the plain-HTTP stack instead.
#>
[CmdletBinding()]
param(
    [switch]$Origin,
    [switch]$PrintOnly
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Resolve-Cloudflared {
    $found = Get-Command cloudflared -ErrorAction SilentlyContinue
    if ($found) { return $found.Source }
    foreach ($candidate in @(
            "$env:ProgramFiles\cloudflared\cloudflared.exe",
            "${env:ProgramFiles(x86)}\cloudflared\cloudflared.exe")) {
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }
    throw "cloudflared not found. Install it with: winget install --id Cloudflare.cloudflared"
}

$cloudflared = Resolve-Cloudflared
# The plain-HTTP stack needs no compose profile; the TLS stack does.
$localUrl = if ($Origin) { 'http://localhost:8080' } else { 'https://localhost:8443' }

# --no-tls-verify is safe HERE ONLY. It applies to the cloudflared -> local nginx
# hop, not to the phone -> Cloudflare edge hop, which uses Cloudflare's own
# publicly trusted certificate. Without it cloudflared rejects the self-signed
# development certificate and every request fails with a 502.
$arguments = @('tunnel', '--url', $localUrl, '--no-autoupdate')
if (-not $Origin) { $arguments += '--no-tls-verify' }

Write-Host ""
Write-Host "DAV tunnel" -ForegroundColor Cyan
Write-Host "  local origin : $localUrl"
Write-Host "  cloudflared  : $cloudflared"
Write-Host ""

if ($PrintOnly) {
    Write-Host "Command:" -ForegroundColor Yellow
    Write-Host "  & `"$cloudflared`" $($arguments -join ' ')" -ForegroundColor DarkGray
    exit 0
}

# Fail fast with an actionable message rather than a confusing 502 later.
if (-not $Origin) {
    $tls = docker compose ps --format '{{.Name}} {{.State}}' 2>$null |
        Where-Object { $_ -like 'dav-frontend-tls*' -and $_ -like '*running*' }
    if (-not $tls) {
        Write-Warning "The TLS container is not running, so the tunnel would return 502."
        Write-Warning "Start it first:  docker compose --profile tls up -d"
        Write-Warning "Continuing anyway in case you are starting it now."
    }
}

Write-Host "Starting tunnel. The public URL is printed once the tunnel is registered." -ForegroundColor Cyan
Write-Host "Open that URL on a phone on ANY network. Stop with Ctrl+C." -ForegroundColor DarkGray
Write-Host ""
Write-Host "Google OAuth: add the printed origin (no trailing slash) to the" -ForegroundColor Yellow
Write-Host "authorized JavaScript origins in the Google Cloud console." -ForegroundColor Yellow
Write-Host "https://console.cloud.google.com/apis/credentials?project=dav-agri" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Phone OTP sign-in needs no Google setup and works right now." -ForegroundColor DarkGray
Write-Host ""

& $cloudflared @arguments
