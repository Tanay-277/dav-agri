import React, { useState } from 'react';
import { TopBar } from '../components/common/TopBar';
import { IrisSphere } from '../components/common/IrisSphere';
import { useStore } from '../state/store';
import { authService } from '../services/authService';
import { getTranslation } from '../i18n';

export const RegisterScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!username.trim() || !password) {
      setError(t.error_occurred);
      return;
    }
    if (password !== confirm) {
      setError(t.error_occurred);
      return;
    }
    setLoading(true);
    try {
      await authService.register(username, password);
      const user = await authService.getCurrentUser();
      store.setUser(user);
      store.routeAfterAuth({ onboarding_completed: user.onboarding_completed });
    } catch (err: any) {
      setError(err.message || t.error_occurred);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full min-h-screen bg-[#e8e5df] flex flex-col items-center justify-between pb-14 select-none">
      <TopBar showBack={true} onBack={() => store.setScreen('login')} showLanguagePill={true} />

      <div className="flex-1 flex items-center justify-center py-4">
        <IrisSphere size={220} />
      </div>

      <form onSubmit={handleSubmit} className="w-full max-w-xs flex flex-col items-center pb-8">
        <h2 className="text-xl font-bold text-stone-900 tracking-tight text-center mb-5">
          {t.register}
        </h2>

        {error && (
          <div className="w-full text-center text-xs text-red-600 bg-red-50 py-2 px-3 rounded-xl mb-3">
            {error}
          </div>
        )}

        <div className="w-full flex flex-col gap-2.5">
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
            autoComplete="new-password"
            className="w-full py-3.5 px-4 rounded-2xl bg-[#d0cac0] text-stone-900 font-semibold text-base placeholder-stone-500 tracking-wider focus:outline-none focus:ring-2 focus:ring-stone-600 shadow-inner"
          />
          <input
            type="password"
            value={confirm}
            onChange={(e) => { setConfirm(e.target.value); setError(null); }}
            placeholder={t.password_confirm}
            autoComplete="new-password"
            className="w-full py-3.5 px-4 rounded-2xl bg-[#d0cac0] text-stone-900 font-semibold text-base placeholder-stone-500 tracking-wider focus:outline-none focus:ring-2 focus:ring-stone-600 shadow-inner"
          />
          <button
            type="submit"
            disabled={loading || !username.trim() || !password || password !== confirm}
            className="w-full py-3.5 px-6 rounded-full border border-stone-400 hover:bg-stone-300/60 text-stone-900 font-semibold text-sm shadow-none active:scale-98 transition-all disabled:opacity-50 disabled:active:scale-100"
          >
            {loading ? t.starting : t.register}
          </button>
        </div>

        <button
          onClick={() => store.setScreen('login')}
          className="mt-4 text-xs text-stone-600 hover:text-stone-800 underline underline-offset-2"
        >
          {t.no_account}
        </button>
      </form>
    </div>
  );
};
