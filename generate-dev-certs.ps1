# Generate a self-signed TLS certificate so the app is served over HTTPS.
#
# WHY THIS EXISTS
# Microphone capture (getUserMedia) is only available in a "secure context".
# Browsers treat https:// and http://localhost as secure; a plain http:// URL on
# a LAN address is NOT. DAV is voice-first, so without HTTPS the microphone is
# blocked on every real handset and the app's primary input disappears.
#
# LIMITATIONS - read before using this anywhere real:
#   * Self-signed => the phone will show a certificate warning and the user must
#     accept it manually. Some browsers treat an untrusted origin as insecure and
#     will still block the microphone.
#   * A real deployment must use a certificate from a trusted CA.
#
# This is a DEVELOPMENT convenience only. See docs/MOBILE.md section 4.

$ErrorActionPreference = "Stop"
$CertDir = Join-Path $PSScriptRoot "certs"
$CertFile = Join-Path $CertDir "dev-cert.crt"
$KeyFile = Join-Path $CertDir "dev-key.key"

if ((Test-Path -LiteralPath $CertFile) -and (Test-Path -LiteralPath $KeyFile)) {
    Write-Host "TLS certificate already exists at $CertDir - nothing to do." -ForegroundColor Green
    exit 0
}

New-Item -ItemType Directory -Path $CertDir -Force | Out-Null

# Collect every LAN address so the cert is valid for whichever one you browse on.
$Addresses = @(
    "localhost",
    "127.0.0.1"
) + (
    Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254*" } |
    ForEach-Object { $_.IPAddress }
) | Sort-Object -Unique

Write-Host "Generating self-signed certificate for:" -ForegroundColor Cyan
$Addresses | ForEach-Object { Write-Host "  - $_" }

# Build a SAN extension: the v1 subjectAltName (IP|dNSName,...) format.
$San = ($Addresses | ForEach-Object {
        if ($_ -match '^\d+\.\d+\.\d+\.\d+$') { "IP:$_" } else { "DNS:$_" }
    }) -join ","

# Locate openssl. Git for Windows bundles one, and is the usual source on
# Windows when it is not on PATH.
function Resolve-OpenSsl {
    if (Get-Command openssl -ErrorAction SilentlyContinue) {
        return (Get-Command openssl).Source
    }
    foreach ($candidate in @(
            "C:\Program Files\Git\usr\bin\openssl.exe",
            "C:\Program Files (x86)\Git\usr\bin\openssl.exe",
            "$env:LOCALAPPDATA\Programs\Git\usr\bin\openssl.exe"
        )) {
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }
    throw "openssl not found. Install Git for Windows (bundles openssl) or add openssl to PATH."
}

$OpenSsl = Resolve-OpenSsl
Write-Host "Using openssl: $OpenSsl" -ForegroundColor DarkGray

$Subject = "CN=dav-localhost"
$Cnf = @"
[req]
distinguished_name = dn
x509_extensions = v3_req
prompt = no

[dn]
CN = dav-localhost

[v3_req]
subjectAltName = $San
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
"@

$CnfPath = Join-Path $env:TEMP "dav-openssl.cnf"
Set-Content -LiteralPath $CnfPath -Value $Cnf -Encoding ASCII

# openssl writes its progress dots to stderr even on success. With
# ErrorActionPreference=Stop that would be treated as a terminating error, so
# relax it around the openssl call and check the exit code instead.
$ErrorActionPreference = "Continue"
& $OpenSsl req -x509 -newkey rsa:2048 -nodes -days 825 `
    -keyout $KeyFile -out $CertFile -config $CnfPath 2>$null | Out-Null
$OpenSslExit = $LASTEXITCODE
$ErrorActionPreference = "Stop"

if ($OpenSslExit -ne 0) {
    throw "openssl failed with exit code $OpenSslExit using: $OpenSsl"
}

Remove-Item -LiteralPath $CnfPath -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Certificate written:" -ForegroundColor Green
Write-Host "  $CertFile"
Write-Host "  $KeyFile"
Write-Host ""
Write-Host "Start the stack with HTTPS enabled:" -ForegroundColor Yellow
Write-Host "  docker compose --profile tls up --build -d"
Write-Host ""
Write-Host "Then open https://<your-LAN-IP>:8443 and accept the certificate warning." -ForegroundColor Yellow
