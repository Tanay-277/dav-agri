import React, { useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { IrisSphere } from '../components/common/IrisSphere';
import { LanguageButton } from '../components/common/LanguageButton';
import { useStore } from '../state/store';

export const LaunchScreen: React.FC = () => {
  const [state, store] = useStore();
  const sessionReady = !state.isRestoring;

  useEffect(() => {
    store.loadInitialData();
  }, []);

  const handleLaunch = () => {
    if (!sessionReady) return;
    store.proceedFromLaunch();
  };

  return (
    <div
      onClick={handleLaunch}
      className="w-full h-full min-h-[100dvh] bg-[#e8e5df] flex flex-col items-center justify-center p-6 select-none relative"
    >
      {/* Language is configurable before sign-in. stopPropagation keeps tapping
          the button from advancing past the splash screen. */}
      <div
        className="absolute top-10 right-6"
        onClick={(e) => e.stopPropagation()}
      >
        <LanguageButton variant="light" />
      </div>

      <div className="flex flex-col items-center justify-center animate-fade-in">
        <IrisSphere
          size={240}
          isPulsing={sessionReady}
          onClick={handleLaunch}
          className={sessionReady ? 'cursor-pointer' : 'cursor-wait'}
        />

        {/* Honest progress state: the splash is doing real work, not just animating. */}
        {!sessionReady && (
          <span className="mt-6 flex items-center gap-2 text-xs font-medium text-stone-500">
            <Loader2 size={14} className="animate-spin" />
            <span>Loading…</span>
          </span>
        )}
      </div>
    </div>
  );
};
