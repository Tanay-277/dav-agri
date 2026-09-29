import React, { useState, useEffect } from 'react';
import { Pause, Play, Mic, Keyboard, AlertCircle } from 'lucide-react';
import { TopBar } from '../components/common/TopBar';
import { IrisSphere } from '../components/common/IrisSphere';
import { WaveformVisualizer } from '../components/voice/WaveformVisualizer';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { queryService } from '../services/queryService';
import { useVoiceRecorder } from '../hooks/useVoiceRecorder';

export const ListeningScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [isManualInput, setIsManualInput] = useState(false);
  const [manualText, setManualText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const defaultSampleQuery =
    state.language === 'en'
      ? 'My cotton production was 12 quintals in 2022, 15 in 2023, 18 in 2024, and 21 in 2025. Show me how my production has changed over the years.'
      : state.language === 'hi'
      ? 'मेरी कपास उत्पादन 2022 में 12 क्विंटल, 2023 में 15, 2024 में 18 और 2025 में 21 थी। उत्पादन में बदलाव समझाएं।'
      : 'माझ्या कापूस उत्पादनाची माहिती आणि खर्चाचा तक्ता समजावून सांगा.';

  const {
    state: voiceState,
    transcript,
    audioLevel,
    errorMessage,
    startRecording,
    stopRecordingAndProcess,
    cancelRecording,
    setTranscript,
  } = useVoiceRecorder({
    language: state.language,
    onResult: (result) => {
      store.setProcessedResult(result.query_response);
      store.setScreen('processed');
    },
    onError: (err) => {
      console.warn('Voice recording fallback available:', err);
    },
  });

  const isRecording = voiceState === 'RECORDING' || voiceState === 'LISTENING';
  const isProcessing =
    voiceState === 'UPLOADING' || voiceState === 'TRANSCRIBING' || voiceState === 'PROCESSING' || isSubmitting;

  useEffect(() => {
    // Start microphone automatically when entering Listening screen
    const timer = setTimeout(() => {
      startRecording();
    }, 400);

    return () => {
      clearTimeout(timer);
      cancelRecording();
    };
  }, []);

  const handleFinishQuery = async () => {
    if (isProcessing) return;

    if (isRecording) {
      setIsSubmitting(true);
      try {
        await stopRecordingAndProcess();
      } catch (e) {
        handleManualFallbackSubmit();
      } finally {
        setIsSubmitting(false);
      }
    } else {
      handleManualFallbackSubmit();
    }
  };

  const handleManualFallbackSubmit = async () => {
    const textToSubmit = (manualText.trim() || transcript.trim() || defaultSampleQuery);
    setIsSubmitting(true);
    try {
      const result = await queryService.executeQuery(textToSubmit, state.language, 'Cotton');
      store.setProcessedResult(result);
      store.setScreen('processed');
    } catch (err) {
      console.error('Query processing error:', err);
      store.setScreen('processed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayText = transcript || (
    isRecording ? (
      state.language === 'mr'
        ? 'माझ्या कापूस उत्पादनाची माहिती आणि खर्चाचा तक्ता समजावून सांगा .....'
        : state.language === 'hi'
        ? 'मेरी कपास उत्पादन और खर्च की स्थिति बताएं .....'
        : 'Show me my cotton production and expense overview .....'
    ) : defaultSampleQuery
  );

  return (
    <div className="w-full h-full min-h-[100dvh] bg-[#e8e5df] flex flex-col justify-between select-none overflow-y-auto">
      {/* Top Bar with Back Arrow */}
      <TopBar showBack={true} onBack={() => store.setScreen('home')} />

      <div className="flex-1 px-5 max-w-sm mx-auto w-full flex flex-col items-center justify-between py-2">
        {/* Status / Title */}
        <div className="text-center">
          <h2 className="text-xl font-bold text-stone-900 tracking-tight">
            {isProcessing ? t.processing : isRecording ? t.listening : t.ready}
          </h2>

          {errorMessage && (
            <div className="flex items-center justify-center gap-1.5 text-xs text-amber-800 bg-amber-100/80 px-3 py-1 rounded-full mt-2">
              <AlertCircle size={13} />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        {/* Center Pulsating Iris Sphere */}
        <div className="my-auto py-3">
          <IrisSphere
            size={220}
            isPulsing={isRecording}
            onClick={handleFinishQuery}
          />
        </div>

        {/* Dynamic Waveform Visualizer */}
        {isRecording && (
          <div className="w-full max-w-xs -mt-2 mb-2">
            <WaveformVisualizer isActive={isRecording} audioLevel={audioLevel} />
          </div>
        )}

        {/* Recognized Live Speech Bubble / Input */}
        <div className="w-full max-w-xs text-center mb-4 px-2">
          {isManualInput ? (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleManualFallbackSubmit();
              }}
              className="w-full"
            >
              <input
                type="text"
                autoFocus
                value={manualText}
                onChange={(e) => setManualText(e.target.value)}
                placeholder={defaultSampleQuery}
                className="w-full py-2.5 px-4 rounded-2xl bg-white border border-stone-300 text-stone-900 text-sm focus:outline-none focus:ring-2 focus:ring-amber-800 shadow-sm"
              />
            </form>
          ) : (
            <p className="text-sm font-semibold text-stone-900 leading-relaxed cursor-pointer" onClick={() => setIsManualInput(true)}>
              {displayText}
            </p>
          )}
        </div>

        {/* Bottom Control Bar */}
        <div className="w-full max-w-xs flex items-center justify-center gap-5 pb-6">
          {/* Pause / Resume Recording */}
          <button
            onClick={() => {
              if (isRecording) {
                cancelRecording();
              } else {
                startRecording();
              }
            }}
            className="w-12 h-12 rounded-full bg-[#d0cac0] hover:bg-[#c4bdb1] flex items-center justify-center text-stone-800 shadow-sm active:scale-95 transition-all"
            title={isRecording ? 'Pause' : 'Resume'}
          >
            {isRecording ? <Pause size={18} className="fill-current" /> : <Play size={18} className="fill-current ml-0.5" />}
          </button>

          {/* Big Center Mic (Tap to stop & execute query) */}
          <button
            onClick={handleFinishQuery}
            disabled={isProcessing}
            className={`w-16 h-16 rounded-full bg-white border-2 border-stone-300 flex items-center justify-center shadow-float active:scale-95 transition-transform ${
              isProcessing ? 'animate-spin' : isRecording ? 'ring-4 ring-amber-700/30' : ''
            }`}
            title="Submit Query"
          >
            <Mic size={24} className={isRecording ? 'text-amber-800' : 'text-stone-900'} />
          </button>

          {/* Keyboard Toggle */}
          <button
            onClick={() => setIsManualInput(!isManualInput)}
            className={`w-12 h-12 rounded-full flex items-center justify-center text-stone-800 shadow-sm active:scale-95 transition-all ${
              isManualInput ? 'bg-amber-800 text-white' : 'bg-[#d0cac0] hover:bg-[#c4bdb1]'
            }`}
            title="Keyboard input"
          >
            <Keyboard size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};
