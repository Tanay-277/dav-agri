import React, { useEffect } from 'react';
import { Mic, ArrowRight } from 'lucide-react';
import { IrisSphere } from '../components/common/IrisSphere';
import { WaveformVisualizer } from '../components/voice/WaveformVisualizer';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { useVoiceRecorder } from '../hooks/useVoiceRecorder';

export const VoiceSetupScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);

  const {
    state: voiceState,
    transcript,
    audioLevel,
    startRecording,
    stopRecordingAndProcess,
    cancelRecording,
  } = useVoiceRecorder({
    language: state.language,
    onResult: () => {
      // Advance once the user has actually spoken a test phrase. This is
      // driven by a real recording, not a timer.
      setTimeout(() => {
        store.setScreen('onboarded');
      }, 1200);
    },
  });

  const isRecording = voiceState === 'RECORDING' || voiceState === 'LISTENING';

  // Recording must NOT start automatically. It previously opened the microphone
  // 600ms after this screen mounted, which meant the app took the mic without a
  // user gesture and then auto-advanced, so onboarding appeared to race through
  // several screens by itself. The user now taps the sphere or the mic button.
  useEffect(() => {
    return () => {
      // Release the mic if the user navigates away mid-recording.
      cancelRecording();
    };
  }, []);

  // The sphere is the primary control for a voice-first app: tap to start
  // recording, tap again to finish. It previously SKIPPED AHEAD to the next
  // screen when idle, so the only way to actually record was a small
  // unlabelled refresh icon - and tapping the big obvious control appeared to
  // move the app forward on its own.
  const handleSphere = () => {
    if (isRecording) {
      stopRecordingAndProcess();
    } else {
      startRecording();
    }
  };

  const handleFinish = () => {
    if (isRecording) {
      stopRecordingAndProcess();
    } else {
      store.setScreen('onboarded');
    }
  };

  return (
    <div className="w-full h-full flex-1 bg-soil flex flex-col items-center justify-between px-6 pt-8 pb-10 select-none text-white overflow-y-auto">
      {/* Top Graphic */}
      <div className="flex-1 flex items-center justify-center py-4">
        <IrisSphere size={220} isPulsing={isRecording} onClick={handleSphere} />
      </div>

      {/* Voice Prompt Section */}
      <div className="w-full max-w-xs flex flex-col items-center gap-4 pb-4">
        <h2 className="text-xl font-bold text-center leading-snug">
          {t.voice_setup_title}
        </h2>

        <p className="text-stone-300 font-medium text-sm text-center min-h-[40px] px-2">
          {transcript ? (
            <span className="text-amber-200 font-semibold">{transcript}</span>
          ) : isRecording ? (
            <span className="text-amber-300/90 animate-pulse">
              {t.voice_setup_listening}
            </span>
          ) : (
            t.voice_setup_prompt
          )}
        </p>

        {/* Dynamic Waveform Visualizer */}
        <div className="w-full mt-1">
          <WaveformVisualizer isActive={isRecording} audioLevel={audioLevel} />
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-4 mt-2">
          {isRecording ? (
            <button
              onClick={handleFinish}
              className="py-3 px-6 rounded-full bg-white text-stone-900 font-bold text-sm shadow-float active:scale-95 flex items-center gap-2"
            >
              <Mic size={16} />
              <span>{t.voice_setup_done}</span>
            </button>
          ) : (
            <button
              onClick={() => startRecording()}
              className="w-12 h-12 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center active:scale-95"
title={t.start_recording}
              aria-label={t.start_recording}
            >
              <Mic size={18} className="text-white" />
            </button>
          )}

          {/* Explicit skip. Voice setup is optional: a farmer on a slow
              connection or with no microphone must still be able to continue,
              and this control used to be an unlabelled arrow. */}
          <button
              onClick={() => {
                store.setScreen('onboarded');
              }}
              aria-label={t.skip_voice_setup}
              className="w-12 h-12 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center active:scale-95 transition-all"
              title={t.skip_voice_setup}
            >
              <ArrowRight size={20} className="text-white" />
            </button>
        </div>
      </div>
    </div>
  );
};
