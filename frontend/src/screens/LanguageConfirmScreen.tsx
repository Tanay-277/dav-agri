import React, { useEffect, useState } from 'react';
import { Check, X, Volume2 } from 'lucide-react';
import { IrisSphere } from '../components/common/IrisSphere';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { voiceService } from '../services/voiceService';

export const LanguageConfirmScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [isPlaying, setIsPlaying] = useState(false);

  const playVerificationAudio = async () => {
    setIsPlaying(true);
    try {
      const sample = await voiceService.getSample(state.language);
      if (sample?.audio_base64) {
        voiceService.playBase64(sample.audio_base64, sample.mime_type || 'audio/mpeg', {
          onEnded: () => setIsPlaying(false),
          onError: () => setIsPlaying(false),
        });
      } else {
        setIsPlaying(false);
      }
    } catch (err) {
      setIsPlaying(false);
    }
  };

  useEffect(() => {
    // Play test phrase when entering screen
    playVerificationAudio();
    return () => {
      voiceService.stopActiveAudio();
    };
  }, [state.language]);

  return (
    <div className="w-full h-full flex-1 bg-soil flex flex-col items-center justify-between px-6 pt-8 pb-10 select-none text-white overflow-y-auto">
      {/* Top Graphic */}
      <div className="flex-1 flex items-center justify-center py-4">
        <IrisSphere size={220} isPulsing={isPlaying} onClick={playVerificationAudio} />
      </div>

      {/* Confirmation Section */}
      <div className="w-full max-w-xs flex flex-col items-center gap-4 pb-6">
        <h2 className="text-lg font-bold text-center leading-snug">
          {t.lang_confirm_title}
        </h2>

        {/* Verification Text Box */}
        <div
          onClick={playVerificationAudio}
          className="w-full p-4 rounded-2xl bg-black/35 border border-white/10 text-stone-200 text-xs text-center leading-relaxed cursor-pointer hover:bg-black/45 transition-colors relative"
        >
          <p className="font-semibold text-white mb-1.5">{t.lang_confirm_sample}</p>
          <div className="flex items-center justify-center gap-1.5 text-amber-200/90 text-[11px] mt-2">
            <Volume2 size={13} className={isPlaying ? 'animate-bounce text-amber-300' : ''} />
            <span>{isPlaying ? t.playing : t.tap_to_hear_again}</span>
          </div>
        </div>

        {/* Actions: Yes (Green) & No (Red) */}
        <div className="w-full flex flex-col gap-2.5 mt-1">
          {/* Green Yes */}
          <button
            onClick={() => {
              voiceService.stopActiveAudio();
              store.setScreen('voice_setup');
            }}
            className="w-full py-3.5 px-6 rounded-full bg-[#1e4620] hover:bg-[#255728] border border-emerald-500/40 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-sm active:scale-98 transition-all"
          >
            <Check size={18} className="text-emerald-400 stroke-[2.5]" />
            <span>{t.yes_can_hear}</span>
          </button>

          {/* Red No */}
          <button
            onClick={() => {
              voiceService.stopActiveAudio();
              store.setScreen('lang_select');
            }}
            className="w-full py-3 px-6 rounded-full bg-[#4a1815] hover:bg-[#5c1e1a] border border-rose-500/40 text-stone-200 font-semibold text-sm flex items-center justify-center gap-2 shadow-sm active:scale-98 transition-all"
          >
            <X size={17} className="text-rose-400 stroke-[2.5]" />
            <span>{t.no_cannot_hear}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
