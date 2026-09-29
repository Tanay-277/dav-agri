import React, { useState, useEffect } from 'react';
import { Play, Volume2, Loader2, AlertCircle } from 'lucide-react';
import { TopBar } from '../components/common/TopBar';
import { IrisSphere } from '../components/common/IrisSphere';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { LanguageCode } from '../types';
import { onboardingService } from '../services/onboardingService';
import { voiceService } from '../services/voiceService';

type AudioState = 'idle' | 'loading' | 'playing' | 'error';

export interface VoicePreviewItem {
  text: string;
  language: LanguageCode;
}

// Explicit Language-to-Speech Preview Mapping
export const voicePreviews: Record<LanguageCode, VoicePreviewItem> = {
  en: {
    text: 'Hello, I am your voice assistant.',
    language: 'en',
  },
  hi: {
    text: 'नमस्ते, मैं आपका वॉइस असिस्टेंट हूँ।',
    language: 'hi',
  },
  mr: {
    text: 'नमस्कार, मी तुमचा व्हॉइस असिस्टंट आहे।',
    language: 'mr',
  },
};

export const LangSelectScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [audioStates, setAudioStates] = useState<Record<LanguageCode, AudioState>>({
    en: 'idle',
    hi: 'idle',
    mr: 'idle',
  });
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      voiceService.stopActiveAudio();
    };
  }, []);

  const handleSelectLanguage = async (lang: LanguageCode) => {
    voiceService.stopActiveAudio();
    store.setLanguage(lang);
    try {
      await onboardingService.confirmLanguage(lang);
    } catch (err) {
      console.warn('Language confirmation queued:', err);
    }
    store.setScreen('language_confirm');
  };

  const handlePlayPreview = async (e: React.MouseEvent, lang: LanguageCode) => {
    e.stopPropagation();
    setErrorMessage(null);

    // If this language is already actively playing, pause/stop it
    if (audioStates[lang] === 'playing') {
      voiceService.stopActiveAudio();
      setAudioStates((prev) => ({ ...prev, [lang]: 'idle' }));
      return;
    }

    // Stop any other active audio
    voiceService.stopActiveAudio();
    setAudioStates({
      en: 'idle',
      hi: 'idle',
      mr: 'idle',
      [lang]: 'loading',
    });

    const preview = voicePreviews[lang];
    console.log(`[TTS_PREVIEW_TRIGGERED] target=${lang} text="${preview.text}" language=${preview.language}`);

    try {
      // 1. Primary: Direct high-fidelity speech synthesis
      const audioBlob = await voiceService.synthesizeSpeech(preview.text, preview.language);
      
      voiceService.playAudioBlob(audioBlob, {
        onPlay: () => {
          setAudioStates({
            en: 'idle',
            hi: 'idle',
            mr: 'idle',
            [lang]: 'playing',
          });
        },
        onEnded: () => {
          setAudioStates((prev) => ({ ...prev, [lang]: 'idle' }));
        },
        onError: (err) => {
          console.error('[TTS_PLAYBACK_ERROR]', err);
          setAudioStates((prev) => ({ ...prev, [lang]: 'error' }));
          setErrorMessage('Voice preview playback failed. Please tap again.');
          setTimeout(() => {
            setAudioStates((prev) => ({ ...prev, [lang]: 'idle' }));
          }, 3000);
        },
      });
    } catch (synthErr) {
      console.warn('[TTS_SYNTH_FALLBACK] Attempting sample fallback endpoint...', synthErr);
      try {
        // 2. Fallback: Pre-computed / sample preview endpoint
        const sample = await voiceService.getSample(preview.language);
        if (!sample || !sample.audio_base64) {
          throw new Error('No audio payload received');
        }

        voiceService.playBase64(sample.audio_base64, sample.mime_type || 'audio/mpeg', {
          onPlay: () => {
            setAudioStates({
              en: 'idle',
              hi: 'idle',
              mr: 'idle',
              [lang]: 'playing',
            });
          },
          onEnded: () => {
            setAudioStates((prev) => ({ ...prev, [lang]: 'idle' }));
          },
          onError: (err) => {
            console.error('[TTS_FALLBACK_ERROR]', err);
            setAudioStates((prev) => ({ ...prev, [lang]: 'error' }));
            setErrorMessage('Voice preview unavailable. Please try again.');
            setTimeout(() => {
              setAudioStates((prev) => ({ ...prev, [lang]: 'idle' }));
            }, 3000);
          },
        });
      } catch (err: any) {
        console.error('[TTS_TOTAL_FAILURE]', err);
        setAudioStates((prev) => ({ ...prev, [lang]: 'error' }));
        setErrorMessage('Unable to connect to the voice service. Please try again.');
        setTimeout(() => {
          setAudioStates((prev) => ({ ...prev, [lang]: 'idle' }));
        }, 3000);
      }
    }
  };

  const languages: { code: LanguageCode; script: string; label: string }[] = [
    { code: 'en', script: 'ABC', label: 'ENGLISH' },
    { code: 'hi', script: 'कखग', label: 'हिन्दी' },
    { code: 'mr', script: 'कखग', label: 'मराठी' },
  ];

  const anyPlaying = Object.values(audioStates).some((s) => s === 'playing');

  return (
    <div className="w-full h-full flex-1 bg-soil flex flex-col items-center justify-between pb-10 select-none text-white overflow-y-auto">
      {/* Top Bar with Back Arrow */}
      <TopBar showBack={true} onBack={() => store.setScreen('signup_options')} showLanguagePill={false} className="text-white" />

      {/* Top Graphic */}
      <div className="flex-1 flex items-center justify-center py-4">
        <IrisSphere size={220} isPulsing={anyPlaying} />
      </div>

      {/* Language Options Section */}
      <div className="w-full max-w-xs flex flex-col items-center gap-3.5 pb-6">
        <h2 className="text-base font-semibold text-stone-200 text-center mb-1">
          {t.choose_voice}
        </h2>

        {errorMessage && (
          <div className="w-full bg-red-900/70 border border-red-500/50 rounded-2xl px-3 py-2 flex items-center gap-2 text-xs text-red-200 mb-1">
            <AlertCircle size={15} className="shrink-0 text-red-300" />
            <span>{errorMessage}</span>
          </div>
        )}

        {languages.map((item) => {
          const isSelected = state.language === item.code;
          const status = audioStates[item.code];

          return (
            <div
              key={item.code}
              onClick={() => handleSelectLanguage(item.code)}
              className={`w-full py-3.5 px-6 rounded-full flex items-center justify-between cursor-pointer transition-all duration-200 shadow-sm active:scale-98 ${
                isSelected
                  ? 'bg-white/25 border border-white/50 text-white'
                  : 'bg-black/35 hover:bg-black/45 border border-white/10 text-stone-200'
              }`}
            >
              <div className="flex items-center gap-4">
                <span className="text-xs font-bold tracking-wider text-amber-200/90 w-8">
                  {item.script}
                </span>
                <span className="text-sm font-semibold tracking-wide">
                  {item.label}
                </span>
              </div>

              {/* Dynamic State Play Preview Button: ▶ → Loading → 🔊 Playing → ▶ */}
              <button
                type="button"
                onClick={(e) => handlePlayPreview(e, item.code)}
                disabled={status === 'loading'}
                className={`w-9 h-9 rounded-full flex items-center justify-center border transition-all ${
                  status === 'playing'
                    ? 'bg-amber-400 border-amber-300 text-stone-950 scale-105 shadow-md shadow-amber-400/30'
                    : status === 'loading'
                    ? 'bg-white/20 border-white/40 text-white'
                    : status === 'error'
                    ? 'bg-red-500/40 border-red-400 text-white'
                    : 'border-white/40 hover:bg-white/20 text-white'
                }`}
                title={`Preview ${item.label} voice`}
              >
                {status === 'loading' ? (
                  <Loader2 size={15} className="animate-spin text-white" />
                ) : status === 'playing' ? (
                  <Volume2 size={16} className="text-stone-950 animate-pulse stroke-[2.5]" />
                ) : (
                  <Play size={13} className="text-white fill-white ml-0.5" />
                )}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
