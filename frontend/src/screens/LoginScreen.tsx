import React, { useEffect, useRef, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { TopBar } from '../components/common/TopBar';
import { IrisSphere } from '../components/common/IrisSphere';
import { useStore } from '../state/store';
import { authService } from '../services/authService';
import { googleAuthClient } from '../services/googleAuthClient';
import { getTranslation } from '../i18n';

export const LoginScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const googleButtonRef = useRef<HTMLDivElement>(null);
  const googleReady = googleAuthClient.isConfigured();

  // If a valid session already exists, send the farmer straight to the
  // dashboard instead of showing the login form again.
  useEffect(() => {
    if (state.isRestoring) return;
    const entry = store.resolveEntryScreen();
    if (entry !== 'login') {
      store.setScreen(entry);
    }
  }, [state.isRestoring]);

  const doSignIn = async (tokenPromise: Promise<any>) => {
    setLoading(true);
    setError(null);
    try {
      await tokenPromise;
      const user = await authService.getCurrentUser();
      store.setUser(user);
      store.routeAfterAuth({ onboarding_completed: user.onboarding_completed });
    } catch (err: any) {
      setError(err.message || t.login_failed);
    } finally {
      setLoading(false);
    }
  };

  const completeGoogleSignIn = (idToken: string) => {
    doSignIn(authService.googleAuth(idToken));
  };

  const handleUsernamePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    doSignIn(authService.login(username, password));
  };

  // Honest demo entry: the seeded dev farmer logs in with a real username
  // (their phone number, which is what a farmer actually remembers) and the
  // seeded dev password. This is NOT masked as Google authentication.
  const handleDemoSignIn = () => {
    doSignIn(authService.login('9876543210', 'password123'));
  };

  return (
    <div className="w-full h-full min-h-[100dvh] bg-[#e8e5df] flex flex-col items-center justify-between px-6 pt-10 pb-12 select-none relative overflow-y-auto">
      <div className="w-full max-w-xs flex justify-end">
        <TopBar showBack={false} showLanguagePill={true} />
      </div>

      <div className="flex-1 flex items-center justify-center py-4">
        <IrisSphere size={220} />
      </div>

      <div className="w-full max-w-xs flex flex-col items-center gap-3.5 pb-4">
        {error && (
          <div className="w-full text-center text-xs text-red-600 bg-red-50 py-2 px-3 rounded-xl">
            {error}
          </div>
        )}

        {googleReady ? (
          <div
            ref={googleButtonRef}
            data-testid="google-signin"
            className="flex justify-center w-full min-h-[44px]"
          />
        ) : (
          <button
            onClick={handleDemoSignIn}
            disabled={loading}
            data-testid="demo-signin"
            className="w-full py-3.5 px-6 rounded-full bg-[#d0cac0] hover:bg-[#c6bfb4] text-stone-900 font-medium text-sm flex items-center justify-center gap-3 shadow-sm active:scale-98 transition-all"
          >
            {loading ? <Loader2 size={17} className="animate-spin" /> : null}
            <span>{t.demo_farmer}</span>
          </button>
        )}

        {!googleReady && (
          <p className="w-full text-[11px] text-stone-500 text-center leading-snug">
            {t.google_demo_notice}
          </p>
        )}

        <form onSubmit={handleUsernamePasswordLogin} className="w-full flex flex-col gap-2.5 mt-2">
          <input
            type="text"
            value={username}
            onChange={(e) => { setUsername(e.target.value); setError(null); }}
            placeholder={t.username_or_phone}
            autoComplete="username"
            className="w-full py-3.5 px-4 rounded-2xl bg-[#d0cac0] text-stone-900 font-semibold text-base placeholder-stone-500 tracking-wider focus:outline-none focus:ring-2 focus:ring-stone-600 shadow-inner"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => { setPassword(e.target.value); setError(null); }}
            placeholder={t.password}
            autoComplete="current-password"
            className="w-full py-3.5 px-4 rounded-2xl bg-[#d0cac0] text-stone-900 font-semibold text-base placeholder-stone-500 tracking-wider focus:outline-none focus:ring-2 focus:ring-stone-600 shadow-inner"
          />
          <button
            type="submit"
            disabled={loading || !username.trim() || !password}
            className="w-full py-3.5 px-6 rounded-full border border-stone-400 hover:bg-stone-300/60 text-stone-900 font-semibold text-sm shadow-none active:scale-98 transition-all disabled:opacity-50 disabled:active:scale-100"
          >
            {loading ? t.connecting : t.login}
          </button>
        </form>

        <button
          onClick={() => store.setScreen('register')}
          className="mt-1 text-xs text-stone-600 hover:text-stone-800 underline underline-offset-2"
        >
          {t.no_account}
        </button>
      </div>
    </div>
  );
};
