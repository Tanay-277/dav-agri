import React, { useState } from 'react';
import { TopBar } from '../components/common/TopBar';
import { IrisSphere } from '../components/common/IrisSphere';
import { useStore } from '../state/store';
import { authService } from '../services/authService';
import { getTranslation } from '../i18n';

export const PhoneScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [phone, setPhone] = useState('9876543210');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length !== 10) {
      setError(
        state.language === 'en'
          ? 'Please enter a valid 10-digit mobile number'
          : state.language === 'hi'
          ? 'कृपया वैध 10-अंकों का मोबाइल नंबर दर्ज करें'
          : 'कृपया वैध 10-अंकी मोबाइल नंबर प्रविष्ट करा'
      );
      return;
    }
    setLoading(true);
    setError(null);

    try {
      await authService.requestOtp(cleaned);
      // Store phone in session or pass via state
      sessionStorage.setItem('dav_pending_phone', cleaned);
      store.setScreen('otp');
    } catch (err: any) {
      setError(err.message || t.error_occurred);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full min-h-screen bg-[#e8e5df] flex flex-col items-center justify-between pb-14 select-none">
      {/* Top Bar with Back Arrow */}
      <TopBar showBack={true} onBack={() => store.setScreen('signup_options')} showLanguagePill={true} />

      {/* Graphic */}
      <div className="flex-1 flex items-center justify-center py-4">
        <IrisSphere size={220} />
      </div>

      {/* Form Section */}
      <form onSubmit={handleSubmit} className="w-full max-w-xs flex flex-col items-center pb-8">
        <h2 className="text-xl font-bold text-stone-900 tracking-tight text-center mb-5">
          {t.enter_phone}
        </h2>

        {error && (
          <div className="w-full text-center text-xs text-red-600 bg-red-50 py-2 px-3 rounded-xl mb-3">
            {error}
          </div>
        )}

        <div className="w-full mb-4 flex items-center gap-2">
          <div className="py-3.5 px-3.5 rounded-2xl bg-[#d0cac0] text-stone-900 font-bold text-sm shadow-inner flex items-center justify-center shrink-0 border border-stone-300/40">
            <span>+91</span>
          </div>
          <input
            type="tel"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={10}
            value={phone}
            onChange={(e) => {
              const digits = e.target.value.replace(/\D/g, '').slice(0, 10);
              setPhone(digits);
            }}
            placeholder="9876543210"
            className="flex-1 py-3.5 px-4 rounded-2xl bg-[#d0cac0] text-stone-900 font-semibold text-base placeholder-stone-500 tracking-wider focus:outline-none focus:ring-2 focus:ring-stone-600 shadow-inner"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3.5 px-6 rounded-full border border-stone-400 hover:bg-stone-300/60 text-stone-900 font-semibold text-sm shadow-none active:scale-98 transition-all"
        >
          {loading ? t.sending_otp : t.login}
        </button>
      </form>
    </div>
  );
};
