/**
 * Google Identity Services (GIS) sign-in.
 *
 * Previously the "Continue with Google" button sent a hardcoded string
 * ('google_token_mock_farmer') to the backend, so no Google account was ever
 * verified. This renders a real Google button when VITE_GOOGLE_CLIENT_ID is
 * configured.
 *
 * When no client ID is set the caller falls back to the demo sign-in, which the
 * backend resolves in development mode. That is deliberately explicit rather
 * than silent: a fake sign-in must never be mistaken for a real one.
 */

const CLIENT_ID = (import.meta as any).env?.VITE_GOOGLE_CLIENT_ID || '';

const GIS_SRC = 'https://accounts.google.com/gsi/client';

let scriptPromise: Promise<void> | null = null;

function loadGis(): Promise<void> {
  if (scriptPromise) return scriptPromise;

  scriptPromise = new Promise((resolve, reject) => {
    if ((window as any).google?.accounts?.id) {
      resolve();
      return;
    }
    const existing = document.querySelector(`script[src="${GIS_SRC}"]`);
    if (existing) {
      existing.addEventListener('load', () => resolve());
      existing.addEventListener('error', () => reject(new Error('Failed to load Google Identity Services')));
      return;
    }
    const script = document.createElement('script');
    script.src = GIS_SRC;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Google Identity Services'));
    document.head.appendChild(script);
  });

  return scriptPromise;
}

export const googleAuthClient = {
  isConfigured(): boolean {
    return Boolean(CLIENT_ID);
  },

  /**
   * Render Google's own button into `elementRef` and resolve with a verified
   * ID token. Never resolves the demo token - the caller decides the fallback.
   */
  /**
   * Render Google's button into `element` and invoke `onCredential` with a
   * verified ID token when the user completes sign-in.
   *
   * A callback is used rather than a returned promise on purpose: this runs
   * once at mount, but the credential arrives later and asynchronously. A
   * returned promise would resolve to nobody, and the sign-in would silently
   * do nothing.
   */
  async renderButton(
    element: HTMLElement,
    onCredential: (idToken: string) => void | Promise<void>,
    onError?: (err: Error) => void
  ): Promise<void> {
    if (!CLIENT_ID) {
      throw new Error('Google Sign-In is not configured (VITE_GOOGLE_CLIENT_ID is unset)');
    }

    await loadGis();
    const google = (window as any).google;

    google.accounts.id.initialize({
      client_id: CLIENT_ID,
      callback: async (response: { credential?: string }) => {
        if (!response?.credential) {
          onError?.(new Error('Google did not return an ID token'));
          return;
        }
        try {
          await onCredential(response.credential);
        } catch (err) {
          onError?.(err instanceof Error ? err : new Error(String(err)));
        }
      },
      ux_mode: 'popup',
    });

    google.accounts.id.renderButton(element, {
      theme: 'outline',
      size: 'large',
      shape: 'pill',
      width: 280,
      text: 'continue_with',
      locale: 'en',
    });
  },
};
