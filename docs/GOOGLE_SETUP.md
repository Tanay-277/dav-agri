# Google Sign-In setup

**Status: everything programmable is configured. One Console click remains —
add the tunnel origin to "Authorised JavaScript origins". That step cannot be
automated (see "Why this is not scriptable").**

## Why this is not scriptable

There is **no `gcloud` command or public Google API** that sets the authorised
JavaScript origins of a standard "Web application" OAuth client. This was
verified, not assumed:

| Attempted | Result |
|---|---|
| `gcloud help --all` / `beta` searched for `oauth`/`credential` | No matching command group in stable |
| `gcloud iam oauth-clients list --project=dav-agri` | Listed **0 items** — that API manages Workforce Identity Federation clients, a different class with no JS-origin concept |
| `gcloud iap oauth-clients` | IAP-branded only; its docs state it "cannot be used as a generic management API for all OAuth clients", and it was deprecated (shutdown Mar 2026) |

The remaining fields are editable only in the Console UI. Google Developers
forum and google-cloud-go issue threads both confirm this for current projects.
So the origin edit is a manual step, not a scripting gap to work around.

The DAV-specific workaround is that **Google Sign-In is optional**: phone OTP
needs no Google configuration at all (§"Phone OTP — no Google setup needed").

## Fix the origins (the one manual step)

The origins entered at creation time were all rejected by Google. Two
distinct errors are shown in the Console:

| Entered | Error | Why |
|---|---|---|
| `https://localhost:8443/` | *URIs must not contain a path or end with `/`* | Trailing slash is not allowed |
| `https://172.16.231.25:8443/` | *Must end with a public top-level domain (such as .com or .org)* | **Google does not allow raw IP addresses** |
| `http://localhost:8080/` | *URIs must not contain a path or end with `/`* | Trailing slash is not allowed |

Open the client and correct them:

    https://console.cloud.google.com/apis/credentials?project=dav-agri

**Authorised JavaScript origins** — remove the trailing slashes:

- `https://localhost:8443`
- `http://localhost:8080`

**Delete `https://172.16.231.25:8443` entirely.** It can never be accepted.

Then add the origin of the tunnel you are testing on, e.g.:

- `https://<random>.trycloudflare.com`

**No trailing slash**, and **no redirect URI is needed** — the frontend uses
Google Identity Services in `popup` mode and sends the ID token straight to the
backend, so only the JavaScript origin is consulted.

### The IP address limitation — this affects phone testing

Google Identity Services requires origins with a **public top-level domain**. A
LAN IP is permanently invalid, not a typo to fix. DAV is a mobile-first app, so
this matters: **Google Sign-In cannot be tested on a phone over a LAN IP.**

To test sign-in on a real handset you need an origin with a real domain. A
Cloudflare tunnel provides one for free and also solves the HTTPS requirement for
the microphone:

```powershell
./start-tunnel.ps1
```

That prints a URL like `https://some-random-words.trycloudflare.com`. Add that
exact origin to the client, then open it on the phone. The tunnel provides both a
public TLD and a trusted certificate.

Because a quick tunnel's hostname **changes on every restart**, a named tunnel on
a real domain is worth setting up before repeated testing — otherwise the origin
must be re-registered each time.

For desktop testing, `https://localhost:8443` is sufficient and works today.

## Phone OTP — no Google setup needed

The app offers **phone OTP sign-in**, which involves Google not at all and so is
unaffected by any of the above. Verified end to end through the tunnel:

```
POST /api/v1/auth/phone/request-otp  {"phone":"9876543210"}   -> 200, expires_in_seconds 300
POST /api/v1/auth/phone/verify-otp   {"phone":"...","otp":"44444"} -> 200, access_token, user_id
GET  /api/v1/auth/me                 Authorization: Bearer <token>    -> 200, Raj Patil, preferred_language mr
```

In development the OTP is the fixed mock code **`44444`**
(`app/otp/mock_provider.py`). Production uses Twilio with a real random code.

So a farmer can complete onboarding on a real handset today, with the
microphone, over the tunnel, without waiting on the Console change.

## Already done

- Google Cloud CLI 587.0.0 installed, on PATH
- Authenticated as `icsarthak9@gmail.com`, the account that owns the project
- Project **`dav-agri`** (number `469952737477`, "DAV Agri") created and set active
- Client ID created: `469952737477-hj87o42kfs03n71fslrfvasc814d8hf0.apps.googleusercontent.com`
- Wired into `frontend/.env`, `backend/.env`, and a root `.env` read by Compose
- Containers rebuilt; the client ID is present in both the bundle and the backend env
- Google's real sign-in button renders (confirmed: Google Identity Services loads
  and injects its iframe; the demo fallback no longer shows)
- Backend token verification is live: it calls
  `https://oauth2.googleapis.com/tokeninfo` and rejects a bad token with
  `Invalid Google authentication token` (confirmed reachable from the container,
  HTTP 400 on a deliberately invalid token)

### Note on the demo sign-in

Once `GOOGLE_CLIENT_ID` is set, the backend **stops** accepting the old
`google_token_mock_farmer` string and verifies every token against Google. That
is deliberate — a mock token must never be accepted by a build that claims to do
real authentication. The grey demo button in the UI only appears when no client
ID is configured at all.

### How the configuration is wired

`docker compose` resolves `${VITE_GOOGLE_CLIENT_ID}` from the shell or from a
`.env` file **next to `docker-compose.yml`**. It does *not* read `backend/.env` or
`frontend/.env`, and both are excluded from the Docker build context by
`.dockerignore`. The root `.env` is therefore the file that actually matters;
without it the build arg and the backend container env both stay empty and the
app silently reverts to the demo sign-in. `configure-google-oauth.ps1` writes all
three.

## Consent screen — required

The app is in **Testing** mode, so **only registered test users can sign in**. If
you are not added as a test user you will get "App is blocked".

    https://console.cloud.google.com/auth/branding?project=dav-agri

- Choose **External**, fill in app name and a contact email
- **Audience** tab → **Test users** → add your own Google account

Changes can take several minutes to propagate.

## Re-running setup

```powershell
./configure-google-oauth.ps1 -ClientId 469952737477-hj87o42kfs03n71fslrfvasc814d8hf0.apps.googleusercontent.com
```

The rebuild is required, not optional: Vite inlines `VITE_*` into the bundle at
build time, so restarting containers would keep serving a bundle with no client ID.

## Verifying

```powershell
docker compose --profile tls logs backend --tail 30 | Select-String "Google OAuth"
```

Expect `Google OAuth [Configured, Client ID: 469952737477-...]`.

In the browser, the sign-in screen should show **Google's own button**. If the
grey DAV button with a "Demo sign-in" caption is still present, the bundle was
not rebuilt. If Google's button appears but sign-in fails with
`origin_mismatch` or `redirect_uri_mismatch`, the origins above are wrong.
