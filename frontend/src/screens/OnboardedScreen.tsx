import React, { useState } from 'react';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { onboardingService } from '../services/onboardingService';

export const OnboardedScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [loading, setLoading] = useState(false);

  const handleStart = async () => {
    setLoading(true);
    try {
      await onboardingService.updateOnboarding({
        onboarding_completed: true,
        voice_confirmed: true,
      });
      if (state.user) {
        store.setUser({
          ...state.user,
          onboarding_completed: true,
        });
      }
    } catch (err) {
      console.warn('Onboarding update queued:', err);
    } finally {
      setLoading(false);
      store.setScreen('weather');
    }
  };

  return (
    <div className="w-full h-full flex-1 bg-soil flex flex-col items-center justify-between px-6 pt-16 pb-12 select-none text-white text-center overflow-y-auto">
      {/* Top Header Message */}
      <div className="w-full pt-2">
        <span className="text-amber-200/90 font-medium text-sm tracking-wide">
          {t.all_ready}
        </span>
      </div>

      {/* Center Motivational Copy */}
      <div className="w-full max-w-xs flex flex-col items-center gap-6 my-auto py-8">
        <h1 className="text-2xl font-bold leading-snug">
          {t.setting_up}
        </h1>

        <p className="text-stone-300 text-sm leading-relaxed max-w-[260px]">
          {t.start_talking_ai}
        </p>
      </div>

      {/* Bottom Start Pill Button */}
      <div className="w-full max-w-xs pb-4">
        <button
          onClick={handleStart}
          disabled={loading}
          className="w-full py-4 px-8 rounded-full bg-white hover:bg-stone-100 text-stone-900 font-bold text-base shadow-float active:scale-98 transition-all"
        >
          {loading ? t.starting : t.get_started}
        </button>
      </div>
    </div>
  );
};
