import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Register the app-shell service worker so the installed app opens reliably on a
// flaky rural connection. API and voice traffic is never cached. Requires a
// secure context (HTTPS or localhost), so this is a no-op over plain http on a
// LAN address - see docs/MOBILE.md.
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch((err) => {
      console.warn('Service worker registration failed:', err);
    });
  });
}
