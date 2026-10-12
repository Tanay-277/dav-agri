import React, { useState, useEffect } from 'react';
import { Pause, Play, Mic, Keyboard, AlertCircle, Loader2, Send } from 'lucide-react';
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
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const {
    state: voiceState,
    transcript,
    audioLevel,
    errorMessage: voiceError,
    startRecording,
    stopRecordingAndProcess,
    cancelRecording,
  } = useVoiceRecorder({
    language: state.language,
    onResult: (result) => {
      store.setProcessedResult(result.query_response);
      store.setScreen('processed');
    },
    onError: (err) => {
      console.warn('Voice recording fallback available:', err);
      setErrorMessage(err);
    },
  });

  const isRecording = voiceState === 'RECORDING' || voiceState === 'LISTENING';
  const isProcessing =
    voiceState === 'UPLOADING' || voiceState === 'TRANSCRIBING' || voiceState === 'PROCESSING' || isSubmitting;

  // Recording must NOT start automatically. It previously opened the microphone
  // 400ms after this screen mounted, so the app took the mic without any user
  // gesture and the first thing a farmer saw was a permission prompt they had
  // not asked for. The sphere and mic button now both toggle recording.
  useEffect(() => {
    return () => {
      // Release the mic if the user navigates away mid-recording.
      cancelRecording();
    };
  }, []);

  // The sphere is the primary control for a voice-first app: tap to start
  // recording, tap again to stop and get the answer. It previously submitted a
  // canned query when idle, so tapping the obvious control produced an answer
  // the farmer never asked for.
  const handleSphere = () => {
    if (isProcessing) return;
    if (isRecording) {
      handleFinishQuery();
    } else {
      startRecording();
    }
  };

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
    } else if (transcript.trim()) {
      // Recorded audio produced no usable transcript, so fall back to text.
      handleManualFallbackSubmit();
    } else {
      // Nothing was said. Start recording rather than answering an invented
      // question: a demo answer is worse than a prompt to speak.
      startRecording();
    }
  };

  const handleManualFallbackSubmit = async () => {
    const textToSubmit = manualText.trim() || transcript.trim();
    if (!textToSubmit) {
      startRecording();
      return;
    }
    setIsSubmitting(true);
    try {
      const result = await queryService.executeQuery(textToSubmit, state.language, 'Cotton');
      store.setProcessedResult(result);
      store.setScreen('processed');
    } catch (err) {
      console.error('Query processing error:', err);
      setErrorMessage(t.query_failed);
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayText = transcript || (
    isRecording ? (
      state.language === 'mr'
        ? 'ऐका आहे... बोला'
        : state.language === 'hi'
        ? 'सुन रहा हूँ... बोलिए'
        : 'Listening... go ahead and speak'
    ) : isProcessing
      ? t.processing
      : t.tap_mic_to_speak
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

          {/* Recorder errors (mic denied, no speech captured) take priority: the hook
            owns them and they explain why nothing is happening. */}
          {(errorMessage || voiceError) && (
            <div className="flex items-center justify-center gap-1.5 text-xs text-amber-800 bg-amber-100/80 px-3 py-1 rounded-full mt-2 max-w-full text-center">
              <AlertCircle size={13} className="shrink-0" />
              <span>{errorMessage || voiceError}</span>
            </div>
          )}
        </div>

        {/* Center Pulsating Iris Sphere */}
        <div className="my-auto py-3">
          <IrisSphere
            size={220}
            isPulsing={isRecording}
            onClick={handleSphere}
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
className="w-full flex items-center gap-2"
            >
              <input
                type="text"
                autoFocus
                enterKeyHint="send"
                value={manualText}
                onChange={(e) => setManualText(e.target.value)}
                placeholder={t.type_your_question}
                aria-label={t.type_your_question}
                className="flex-1 min-w-0 py-2.5 px-4 rounded-2xl bg-white border border-stone-300 text-stone-900 text-sm focus:outline-none focus:ring-2 focus:ring-amber-800 shadow-sm"
              />
              {/* An explicit send button, not just the Enter key: on a phone the
                  keyboard's return key is easy to miss, and with no visible
                  control there was no obvious way to submit. */}
              <button
                type="submit"
                disabled={!manualText.trim() || isProcessing}
                aria-label={t.ask}
                className="w-11 h-11 shrink-0 rounded-full bg-stone-800 text-white flex items-center justify-center shadow-sm active:scale-95 transition-transform disabled:opacity-40"
              >
                {isProcessing ? <Loader2 size={17} className="animate-spin" /> : <Send size={17} />}
              </button>
            </form>
          ) : (
            /* Tapping the transcript opens the keyboard, which is the only way
               to edit or submit by hand. It is labelled as an action rather
               than looking like static explanatory text. */
            <button
              type="button"
              onClick={() => setIsManualInput(true)}
              className="w-full text-sm font-semibold text-stone-900 leading-relaxed text-center"
            >
              {displayText}
            </button>
          )}
        </div>

        {/* Bottom Control Bar */}
        <div className="w-full max-w-xs flex items-center justify-center gap-5 pb-6">
          {/* Pause / Resume Recording */}
          <button
            onClick={() => {
              if (isProcessing) return;
              if (isRecording) {
                handleFinishQuery();
              } else {
                startRecording();
              }
            }}
            className="w-12 h-12 rounded-full bg-[#d0cac0] hover:bg-[#c4bdb1] flex items-center justify-center text-stone-800 shadow-sm active:scale-95 transition-all"
            title={isRecording ? t.stop_recording : t.start_recording}
            aria-label={isRecording ? t.stop_recording : t.start_recording}
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
            aria-label={isRecording ? t.stop_and_send : t.start_recording}
          >
            <Mic size={24} className={isRecording ? 'text-amber-800' : 'text-stone-900'} />
          </button>

          {/* Keyboard Toggle */}
          <button
            type="button"
            onClick={() => setIsManualInput(!isManualInput)}
            aria-label={t.type_instead}
            className={`w-12 h-12 rounded-full flex items-center justify-center text-stone-800 shadow-sm active:scale-95 transition-all ${
              isManualInput ? 'bg-amber-800 text-white' : 'bg-[#d0cac0] hover:bg-[#c4bdb1]'
            }`}
          >
            <Keyboard size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};
