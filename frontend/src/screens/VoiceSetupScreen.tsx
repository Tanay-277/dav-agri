import React, { useEffect } from 'react';
import { Mic, ArrowRight, RefreshCw } from 'lucide-react';
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
      // Auto advance to Onboarded screen after successful test
      setTimeout(() => {
        store.setScreen('onboarded');
      }, 1200);
    },
  });

  const isRecording = voiceState === 'RECORDING' || voiceState === 'LISTENING';

  useEffect(() => {
    // Automatically trigger mic setup/test after brief delay
    const timer = setTimeout(() => {
      startRecording();
    }, 600);
    return () => {
      clearTimeout(timer);
      cancelRecording();
    };
  }, []);

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
        <IrisSphere size={220} isPulsing={isRecording} onClick={handleFinish} />
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
              title="Record again"
            >
              <RefreshCw size={18} className="text-white" />
            </button>
          )}

          <button
            onClick={() => store.setScreen('onboarded')}
            className="w-12 h-12 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center active:scale-95 transition-all"
            title="Continue"
          >
            <ArrowRight size={20} className="text-white" />
          </button>
        </div>
      </div>
    </div>
  );
};
