# DAV — Mobile-First Web Application Contract

**Status:** Normative. This document defines the *intended access model* of DAV and the
constraints every change must preserve.

DAV is a **mobile-first web application**. The primary user opens a URL in a mobile
browser (Android Chrome, iOS Safari) and uses the app directly. It is **not** a desktop
application that merely happens to be responsive, and it is **not** a native app.

If a change makes DAV harder to use as "a URL opened on a phone", it is out of scope
unless this document is updated in the same change.

---

## 1. The Access Model

```
   Farmer's phone (primary)          Farmer's phone (secondary)
   ┌──────────────────────┐          ┌──────────────────────┐
   │ Android Chrome      │          │ iOS Safari           │
   │  opens  <url>       │          │  opens  <url>        │
   └──────────┬───────────┘          └──────────┬───────────┘
              │ HTTPS (REQUIRED)                 │
              │ same-origin /api/v1/*            │
              ▼                                  ▼
   ┌───────────────────────────────────────────────────────┐
   │            DAV FastAPI Backend  /api/v1/*              │
   │   Voice (STT/TTS) · Weather · Farm Analytics · Auth   │
   └───────────────────────────────────────────────────────┘
```

Non-negotiable properties of this model:

| # | Property | Why it matters |
|---|---|---|
| P1 | **Users never install anything.** No app store, no APK, no `npm`. | The whole onboarding funnel is a URL + OTP/Google tap. |
| P2 | **The browser mic is the primary input.** | DAV is voice-*first*; a phone without mic access is a broken client, not a degraded one. |
| P3 | **Works on a real handset over a real network.** | Wi-Fi LAN during testing, internet in the field. |
| P4 | **Dev and prod share one API contract.** | No separate mobile backend. `/api/v1/*` is identical everywhere. |

---

## 2. Verified Current State

Checked against this repository on 2026-09-30.

### Working

- **Viewport is already mobile-correct.** `frontend/index.html:6` sets
  `width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover`.
  `viewport-fit=cover` is required for notches; the rest matches the fixed phone-width
  layout built from the 17-screen Figma design.
- **Dev server is reachable from a phone.** `frontend/vite.config.ts:8` sets `host: true`,
  so Vite binds all interfaces. Confirmed live: `http://172.16.231.25:5173/` returned HTTP 200.
- **STT/TTS work server-side.** `POST /api/v1/voice/synthesize` and
  `GET /api/v1/voice/sample` return real audio for `en`/`hi`/`mr`.

### Resolved

| ID | Issue | Fix |
|----|-------|-----|
| **M1** | API base URL was pinned to `localhost` — on a phone, `localhost` means the phone itself | `apiClient.ts` now defaults to the relative `/api/v1`, so the app calls whichever origin served it. Verified: the built bundle contains no `localhost:8000`. |
| **M2** | Backend CORS rejected LAN origins (verified: no `Access-Control-Allow-Origin` header) | The app is now **same-origin** through nginx, so CORS is not exercised at all. The backend also accepts `CORS_ORIGINS=*` for direct access, since a phone's LAN address is dynamic. Credentials are disabled in that mode, because the CORS spec forbids `*` with credentials and DAV uses a Bearer header, not a cookie. |
| **M3** | No HTTPS, so `getUserMedia` was unavailable on any non-localhost host | Solved two ways. Locally, `generate-dev-certs.ps1` issues a self-signed cert covering `localhost` and every current LAN IP, and the `tls` compose profile serves HTTPS and redirects HTTP → HTTPS. For a **real handset**, use `start-tunnel.ps1`, which publishes a trusted public HTTPS origin (see §2.2). |
| **M4** | Not installable to a home screen | Added `manifest.webmanifest`, a service worker, generated icons (192/512/maskable/180), and Apple meta tags. Registered in `main.tsx`. |
| **M5** | `/api/v1/openapi.json` redirected to `/openapi.json`, which nginx did not proxy, so the SPA fallback answered with `index.html` and JSON parsing failed | nginx now proxies `/openapi.json` and `/redoc` in both `nginx.conf` and `nginx-tls.conf`. Verified: `application/json`, 26 paths. |

---

## 2.1 Running the Stack

```bash
# HTTP only - fine for UI work, but the microphone is blocked on a real phone.
docker compose up --build -d            # app on :8080

# HTTPS - required to test the microphone on a real handset.
./generate-dev-certs.ps1                # once; writes ./certs
docker compose --profile tls up --build -d
```

| URL | Purpose |
|-----|---------|
| `http://localhost:8080` | App, plain HTTP (no mic on a phone) |
| `https://<LAN-IP>:8443` | App over HTTPS, self-signed — desktop testing only |
| `https://<tunnel>.trycloudflare.com` | **Real handset testing — use this for the mic** (§2.2) |
| `https://<LAN-IP>:8443/docs` | Swagger UI, proxied to the backend |
| `http://localhost:8001/health` | Backend health, published for debugging |

Two notes on the local setup:

- The backend is published on **host port 8001**, not 8000, because 8000 is
  frequently already taken on developer machines. The port is only a
  convenience — the app reaches the backend same-origin through nginx.
- A self-signed certificate triggers a browser warning the farmer must accept.
  Some browsers treat an untrusted origin as insecure and will still block the
  microphone. **Use the tunnel in §2.2 for a real handset.**

---

## 2.2 Testing the Microphone on a Real Handset

This is the part that cannot be faked. A plain `http://` LAN address is not a
secure context, and a self-signed certificate is usually treated as untrusted, so
in both cases `getUserMedia` is denied. The reliable fix is to give the phone a
**trusted public HTTPS origin** with a Cloudflare quick tunnel:

```powershell
docker compose --profile tls up -d   # local TLS origin on :8443
./start-tunnel.ps1                   # prints https://<random>.trycloudflare.com
```

Open the printed URL on the phone. It works from **any network**, not just the
same Wi-Fi, because the request no longer depends on the LAN at all.

### Why this satisfies both the browser and Google

| Requirement | Why the tunnel solves it |
|---|---|
| `getUserMedia` needs a secure context | The phone sees real `https://` with a Google Trust Services certificate, so the origin is trusted. |
| The user must not accept a cert warning | The phone terminates TLS at Cloudflare's edge, so the self-signed development certificate is never presented. It stays on the local hop. |
| Google OAuth rejects raw-IP origins | `https://<hostname>.trycloudflare.com` is a real hostname, not an IP, so it is valid as an authorized JavaScript origin. |

Traffic is encrypted on both hops: phone → Cloudflare edge, and cloudflared →
local nginx. The `--no-tls-verify` flag in the script applies **only** to the
second, local hop, so that cloudflared tolerates the self-signed development
certificate. It does not weaken the phone-facing hop. Without it, cloudflared
rejects the origin certificate and every request returns 502.

### Verified behaviour

Measured in real Chrome (v154) driven over CDP against the live tunnel:

| Origin | `isSecureContext` | `getUserMedia` |
|---|---|---|
| `https://<tunnel>.trycloudflare.com` | `true` | **OK** — live microphone track returned |
| `http://<LAN-IP>:8080` | `false` | **API unavailable** — `navigator.mediaDevices` is undefined |

`GET /health`, `GET /openapi.json` (26 paths, real JSON), `/docs`, `/redoc`, the
manifest, and `GET /api/v1/voice/sample?language=mr` all return 200 through the
tunnel, so the app, the API, and the service worker are all same-origin there.

### Two things to know about quick tunnels

1. **The hostname changes on every restart.** Add each new origin to the Google
   Cloud console, with no trailing slash. This is the main friction of quick
   tunnels; a named tunnel on a real domain removes it.
2. **There is no uptime guarantee.** Quick tunnels are for testing. Production
   needs a named tunnel or a normal public deployment — see the production
   requirements below.

---

## 3. Rules for Contributors

These are the constraints to hold when writing code. Violating one silently breaks the
mobile experience while leaving desktop development looking perfectly fine.

1. **Never hardcode a host.** The client calls the relative `/api/v1`. Do not
   reintroduce an absolute default — on a phone it would point at the device itself.
2. **Keep API calls same-origin.** Both the nginx container and the Vite dev server
   proxy `/api/v1`. This is what removed the CORS and host-resolution class of bugs.
3. **Never remove `viewport-fit=cover` or reintroduce `user-scalable=yes`-style zooming
   gaps** — the 17 screens are laid out at a fixed phone width.
4. **Any new audio path must negotiate mobile codecs.** `useVoiceRecorder.ts:101-112`
   already probes `audio/webm;codecs=opus` → `audio/mp4` → `audio/aac` → `audio/ogg` in that
   order. iOS Safari needs `audio/mp4`; desktop-only `audio/webm` will not record on iPhone.
5. **Do not add desktop-only affordances** (hover-only menus, mouse-dependent drag, keyboard
   shortcuts) without a touch equivalent. The primary target has no hover and no keyboard.
6. **Never cache API or voice responses in the service worker.** A replayed STT/TTS
   response is a wrong answer delivered confidently. `public/sw.js` passes `/api/`
   straight to the network for exactly this reason; keep it that way.
7. **Bump `CACHE_VERSION` in `public/sw.js`** whenever the app shell changes, or users
   stay pinned to a stale build.

---

## 4. Running and Testing on a Phone

### Without Docker

The Vite dev server proxies `/api/v1` to the backend, so no absolute host is
needed. Start both, then open the dev server **by LAN IP**:

```bash
cd backend  && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
cd frontend && npm run dev     # prints a Network: http://<LAN-IP>:5173/
```

This covers the UI and voice playback. **It cannot test the microphone** — a plain
`http://` LAN address is not a secure context. For that, use the tunnel in §2.2.

### With Docker (recommended)

See §2.1 and §2.2. For a real handset, run `docker compose --profile tls up -d`
and then `./start-tunnel.ps1`, and open the printed public URL.

### Verifying on a real device

1. Run `docker compose --profile tls up -d`, then `./start-tunnel.ps1`.
2. Open the printed `https://<random>.trycloudflare.com` URL on the phone. No
   certificate warning should appear — that is the point of the tunnel.
3. Add that exact origin (no trailing slash) to the Google OAuth authorized
   JavaScript origins if you are testing Google sign-in.
4. Confirm: language previews play audio, and holding the mic button records with
   no permission error.
5. Check the console: `Failed to fetch` means a host/CORS problem; a
   `getUserMedia` unavailability error means the origin is not a secure context.
6. Confirm installability: Chrome menu → "Add to Home screen"; iOS Safari →
   Share → "Add to Home Screen".

Only step 2 is allowed to be skipped on a desktop machine. Steps 4-6 must be
confirmed on the handset, because `getUserMedia` and PWA install prompts behave
differently there.

### Production requirements

- Terminate TLS with a **trusted CA certificate** — mandatory for the microphone.
  The tunnel in §2.2 satisfies this for testing; production should serve DAV from
  a real public hostname with a real certificate instead of a quick tunnel.
- Serve `frontend/dist` from a static host or CDN behind the same origin as `/api`,
  or pin `CORS_ORIGINS` to the exact production origin.
- Set `APP_SECRET_KEY` and `JWT_SECRET` to real values; `app/core/config.py`
  refuses to boot with the dev defaults when `ENVIRONMENT=production`.
- Do not expose the backend port publicly — the frontend proxy is the only
  intended entry point.
- Replace the quick tunnel with a **named** Cloudflare tunnel bound to a stable
  domain, so the Google OAuth origin and any installed PWA stop changing on every
  restart.

---

## 5. Offline behaviour

The service worker caches the **app shell only** (HTML, hashed assets, icons), so an
installed app opens instantly and survives a dropped connection. It will show the
app while the network is down, but it will not answer farming questions — those
require live weather and voice services.

API and voice traffic is explicitly passed through to the network. This is
deliberate: a cached STT/TTS response would replay a stale answer as though it
were current, which is worse for a farmer than a visible error.

---

## 6. Related Documents

- [Architecture](ARCHITECTURE.md) — component boundaries and system topology
- [Voice Pipeline](VOICE.md) — STT/TTS design
- [REST API](API.md) — endpoint contracts
- [Setup](SETUP.md) — local development