import React, { useState } from 'react';
import { Phone, X, AlertCircle, ArrowRight } from 'lucide-react';
import { IrisSphere } from '../components/common/IrisSphere';
import { useStore } from '../state/store';
import { authService } from '../services/authService';
import { getTranslation } from '../i18n';

export const SignupOptionsScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showGoogleNotice, setShowGoogleNotice] = useState(false);

  const handleGoogleSignInProceed = async () => {
    setShowGoogleNotice(false);
    setLoading(true);
    setError(null);
    try {
      const res = await authService.googleAuth('google_token_mock_farmer');
      const user = await authService.getCurrentUser();
      store.setUser(user);
      // Always go through onboarding flow regardless of onboarding_completed status
      store.setScreen('lang_select');
    } catch (err: any) {
      setError(err.message || 'Google sign-in failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-full min-h-[100dvh] bg-[#e8e5df] flex flex-col items-center justify-between px-6 pt-10 pb-12 select-none relative overflow-y-auto">
      {/* Top Graphic: Signature Iris Sphere */}
      <div className="flex-1 flex items-center justify-center py-4">
        <IrisSphere size={220} />
      </div>

      {/* Bottom Action Section */}
      <div className="w-full max-w-xs flex flex-col items-center gap-3.5 pb-4">
        {error && (
          <div className="w-full text-center text-xs text-red-600 bg-red-50 py-2 px-3 rounded-xl">
            {error}
          </div>
        )}

        {/* 1. Continue with Google */}
        <button
          onClick={() => setShowGoogleNotice(true)}
          disabled={loading}
          className="w-full py-3.5 px-6 rounded-full bg-[#d0cac0] hover:bg-[#c6bfb4] text-stone-900 font-medium text-sm flex items-center justify-center gap-3 shadow-sm active:scale-98 transition-all"
        >
          {/* Google "G" icon */}
          <svg width="18" height="18" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.65v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.14z"
            />
            <path
              fill="#34A853"
              d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.24v3.15C3.26 21.36 7.34 24 12 24z"
            />
            <path
              fill="#FBBC05"
              d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.24C.45 8.16 0 9.98 0 12s.45 3.84 1.24 5.42l4.04-3.15z"
            />
            <path
              fill="#EA4335"
              d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.24 6.58l4.04 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
            />
          </svg>
          <span>{loading ? t.connecting : t.continue_google}</span>
        </button>

        {/* 2. Sign up with phone */}
        <button
          onClick={() => store.setScreen('phone')}
          className="w-full py-3.5 px-6 rounded-full bg-[#d0cac0] hover:bg-[#c6bfb4] text-stone-900 font-medium text-sm flex items-center justify-center gap-3 shadow-sm active:scale-98 transition-all"
        >
          <Phone size={17} className="text-stone-800" />
          <span>{t.signup_phone}</span>
        </button>

        {/* 3. Log in */}
        <button
          onClick={() => store.setScreen('phone')}
          className="w-full py-3 px-6 rounded-full border border-stone-400/80 hover:bg-stone-300/40 text-stone-800 font-medium text-sm text-center shadow-none active:scale-98 transition-all mt-1"
        >
          {t.login}
        </button>
      </div>

      {/* Google OAuth Configuration Notice Modal */}
      {showGoogleNotice && (
        <div className="absolute inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-6">
          <div className="bg-white rounded-3xl p-6 max-w-xs w-full shadow-2xl flex flex-col gap-4 border border-stone-200">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2 text-stone-900 font-bold text-sm">
                <AlertCircle size={18} className="text-amber-600" />
                <span>{t.google_notice_title}</span>
              </div>
              <button
                onClick={() => setShowGoogleNotice(false)}
                className="text-stone-400 hover:text-stone-600"
              >
                <X size={16} />
              </button>
            </div>

            <p className="text-xs text-stone-600 leading-relaxed">
              {t.google_notice_desc}
            </p>

            <div className="flex flex-col gap-2 pt-2">
              <button
                onClick={handleGoogleSignInProceed}
                className="w-full py-2.5 px-4 rounded-full bg-stone-900 text-white font-semibold text-xs flex items-center justify-center gap-2 active:scale-98"
              >
                <span>{t.continue_google}</span>
                <ArrowRight size={14} />
              </button>

              <button
                onClick={() => {
                  setShowGoogleNotice(false);
                  store.setScreen('phone');
                }}
                className="w-full py-2 px-4 rounded-full border border-stone-300 text-stone-700 font-medium text-xs text-center active:scale-98"
              >
                {t.use_phone_number}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
