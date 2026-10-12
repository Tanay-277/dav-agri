import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Bind all interfaces so a phone on the same Wi-Fi can load the dev server.
    host: true,
    // Proxy the API on the same origin so the client never needs an absolute host.
    // Mirrors the nginx setup used by docker-compose.
    proxy: {
      '/api/v1': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});
