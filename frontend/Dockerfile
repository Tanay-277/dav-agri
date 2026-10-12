# ---- build stage ----
FROM node:22-slim AS build

WORKDIR /app

# Required for Vite's esbuild binary.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 make g++ ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund

COPY . .

# Relative base URL: the browser calls /api/v1 on the same origin that served
# the app, so no host is ever embedded and no absolute URL can be wrong on a
# phone. See docs/MOBILE.md.
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Public Google OAuth client ID, baked in at build time. Empty means the app
# uses the development demo sign-in. Safe to expose - it is a public identifier.
ARG VITE_GOOGLE_CLIENT_ID=
ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID

RUN npm run build

# ---- serve stage ----
FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Alternate TLS-terminating server config, mounted over conf.d/default.conf by
# the tls compose profile:  docker compose --profile tls up --build -d
COPY nginx-tls.conf /etc/nginx/nginx-tls.conf

EXPOSE 80 443

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]