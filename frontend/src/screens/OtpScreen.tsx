import React, { useState, useRef } from 'react';
import { TopBar } from '../components/common/TopBar';
import { IrisSphere } from '../components/common/IrisSphere';
import { useStore } from '../state/store';
import { authService } from '../services/authService';
import { profileService } from '../services/profileService';
import { getTranslation } from '../i18n';

export const OtpScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [digits, setDigits] = useState<string[]>(['4', '4', '4', '4', '4']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const phone = sessionStorage.getItem('dav_pending_phone') || '9876543210';
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleDigitChange = (index: number, val: string) => {
    if (val.length > 1) {
      val = val.slice(-1);
    }
    const newDigits = [...digits];
    newDigits[index] = val;
    setDigits(newDigits);

    // Auto advance focus
    if (val && index < 4) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerify = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const otpCode = digits.join('');
    if (otpCode.length < 5) {
      setError(t.enter_all_otp_digits);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await authService.verifyOtp(phone, otpCode);
      const user = await authService.getCurrentUser();
      store.setUser(user);
      const profile = await profileService.getProfile();
      store.setProfile(profile);

      // Transition strictly to Language Select
      store.setScreen('lang_select');
    } catch (err: any) {
      setError(err.message || t.error_occurred);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full min-h-screen bg-[#e8e5df] flex flex-col items-center justify-between pb-14 select-none">
      {/* Top Bar with Back Arrow */}
      <TopBar showBack={true} onBack={() => store.setScreen('phone')} showLanguagePill={true} />

      {/* Graphic */}
      <div className="flex-1 flex items-center justify-center py-4">
        <IrisSphere size={220} />
      </div>

      {/* Form Section */}
      <div className="w-full max-w-xs flex flex-col items-center pb-8">
        <h2 className="text-xl font-bold text-stone-900 tracking-tight text-center mb-6">
          {t.enter_otp}
        </h2>

        {error && (
          <div className="w-full text-center text-xs text-red-600 bg-red-50 py-2 px-3 rounded-xl mb-3">
            {error}
          </div>
        )}

        {/* 5 Digit Input Boxes */}
        <div className="flex items-center justify-center gap-2.5 mb-6">
          {digits.map((digit, idx) => (
            <input
              key={idx}
              ref={(el) => {
                inputRefs.current[idx] = el;
              }}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleDigitChange(idx, e.target.value)}
              onKeyDown={(e) => handleKeyDown(idx, e)}
              className="w-12 h-12 text-center text-lg font-bold rounded-2xl bg-[#d0cac0] text-stone-900 focus:outline-none focus:ring-2 focus:ring-stone-600 shadow-inner"
            />
          ))}
        </div>

        {/* Verify OTP Button */}
        <button
          onClick={() => handleVerify()}
          disabled={loading}
          className="w-full py-3.5 px-6 rounded-full border border-stone-400 hover:bg-stone-300/60 text-stone-900 font-semibold text-sm shadow-none active:scale-98 transition-all"
        >
          {loading ? t.verifying : t.verify_otp}
        </button>
      </div>
    </div>
  );
};
