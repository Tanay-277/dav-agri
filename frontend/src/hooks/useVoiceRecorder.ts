import { useState, useRef, useCallback, useEffect } from 'react';
import { LanguageCode } from '../types';
import { voiceService, VoiceQueryResult } from '../services/voiceService';

export type VoiceState =
  | 'IDLE'
  | 'LISTENING'
  | 'RECORDING'
  | 'UPLOADING'
  | 'TRANSCRIBING'
  | 'PROCESSING'
  | 'RESPONSE'
  | 'PLAYING_AUDIO'
  | 'COMPLETED'
  | 'ERROR';

interface UseVoiceRecorderOptions {
  language?: LanguageCode;
  onTranscriptChange?: (text: string) => void;
  onResult?: (result: VoiceQueryResult) => void;
  onError?: (error: string) => void;
}

export function useVoiceRecorder({
  language = 'mr',
  onTranscriptChange,
  onResult,
  onError,
}: UseVoiceRecorderOptions = {}) {
  const [state, setState] = useState<VoiceState>('IDLE');
  const [transcript, setTranscript] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [audioLevel, setAudioLevel] = useState<number>(0);
  const [isPermissionGranted, setIsPermissionGranted] = useState<boolean>(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const currentAudioElementRef = useRef<HTMLAudioElement | null>(null);

  // Map app language code to BCP-47 speech recognition tag
  const getBcp47 = (lang: LanguageCode): string => {
    switch (lang) {
      case 'mr':
        return 'mr-IN';
      case 'hi':
        return 'hi-IN';
      case 'en':
      default:
        return 'en-IN';
    }
  };

  // Structured Logging
  const logToken = (token: string, payload?: any) => {
    if (payload !== undefined) {
      console.log(`[VOICE_PIPELINE] [${token}]`, payload);
    } else {
      console.log(`[VOICE_PIPELINE] [${token}]`);
    }
  };

  // Cleanup active audio tracks and context
  const cleanupMedia = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (_) {}
      recognitionRef.current = null;
    }
    if (currentAudioElementRef.current) {
      currentAudioElementRef.current.pause();
      currentAudioElementRef.current = null;
    }
    setAudioLevel(0);
  }, []);

  useEffect(() => {
    return () => {
      cleanupMedia();
    };
  }, [cleanupMedia]);

  // Determine best supported recording MIME type across modern browsers & iOS Safari
  const getSupportedMimeType = (): string => {
    if (typeof MediaRecorder === 'undefined') return '';
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/aac',
      'audio/ogg;codecs=opus',
      'audio/wav',
    ];
    for (const t of types) {
      if (MediaRecorder.isTypeSupported(t)) {
        return t;
      }
    }
    return '';
  };

  // Audio level monitor for waveform/visualizer
  const setupAudioAnalyser = (stream: MediaStream) => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      audioContextRef.current = ctx;
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 64;
      source.connect(analyser);
      analyserRef.current = analyser;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        analyser.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const avg = sum / dataArray.length;
        setAudioLevel(Math.min(1.0, avg / 128.0));
        animFrameRef.current = requestAnimationFrame(tick);
      };
      tick();
    } catch (e) {
      console.warn('AudioAnalyser setup failed:', e);
    }
  };

  // Setup browser SpeechRecognition if available
  const setupSpeechRecognition = (langCode: LanguageCode, onLiveText: (text: string) => void) => {
    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRec) {
      return null;
    }

    try {
      const rec = new SpeechRec();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = getBcp47(langCode);

      rec.onresult = (event: any) => {
        let interimText = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          interimText += event.results[i][0].transcript;
        }
        if (interimText.trim()) {
          onLiveText(interimText.trim());
        }
      };

      rec.onerror = (e: any) => {
        // Recognition errors do not block audio recording
        console.warn('SpeechRecognition error:', e.error);
      };

      rec.start();
      return rec;
    } catch (e) {
      console.warn('Failed to start browser SpeechRecognition:', e);
      return null;
    }
  };

  // Start recording
  const startRecording = useCallback(async () => {
    cleanupMedia();
    setErrorMessage(null);
    setTranscript('');
    audioChunksRef.current = [];

    setState('LISTENING');

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Microphone access is not supported by your browser.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      logToken('MIC_PERMISSION_GRANTED');
      setIsPermissionGranted(true);
      streamRef.current = stream;

      setupAudioAnalyser(stream);

      // Start live speech recognition
      recognitionRef.current = setupSpeechRecognition(language, (liveText) => {
        setTranscript(liveText);
        onTranscriptChange?.(liveText);
      });

      const mimeType = getSupportedMimeType();
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstart = () => {
        setState('RECORDING');
        logToken('RECORDING_STARTED', { mimeType: recorder.mimeType });
      };

      recorder.onerror = (err) => {
        console.error('MediaRecorder error:', err);
        setState('ERROR');
        setErrorMessage('Recording failed. Please try again.');
        onError?.('Recording failed.');
      };

      recorder.start(250); // Slice data every 250ms
    } catch (err: any) {
      console.error('Microphone error:', err);
      setState('ERROR');
      const msg = err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError'
        ? 'Microphone permission denied. Please allow microphone access in your browser settings.'
        : err.message || 'Could not access microphone.';
      setErrorMessage(msg);
      onError?.(msg);
      cleanupMedia();
    }
  }, [language, cleanupMedia, onError, onTranscriptChange]);

  // Stop recording and process query
  const stopRecordingAndProcess = useCallback(async () => {
    if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
      return;
    }

    const recorder = mediaRecorderRef.current;

    return new Promise<void>((resolve) => {
      recorder.onstop = async () => {
        logToken('RECORDING_STOPPED');
        if (recognitionRef.current) {
          try {
            recognitionRef.current.stop();
          } catch (_) {}
        }

        const mimeType = recorder.mimeType || 'audio/webm';
        const finalBlob = new Blob(audioChunksRef.current, { type: mimeType });
        logToken('AUDIO_SIZE', `${finalBlob.size} bytes (${mimeType})`);

        if (finalBlob.size === 0) {
          setState('ERROR');
          setErrorMessage('No audio recorded. Please speak clearly into your microphone.');
          cleanupMedia();
          resolve();
          return;
        }

        try {
          setState('UPLOADING');
          logToken('UPLOAD_STARTED');

          logToken('STT_STARTED');
          setState('TRANSCRIBING');

          logToken('QUERY_STARTED');
          setState('PROCESSING');

          const response = await voiceService.sendVoiceQuery(finalBlob, language, true);
          logToken('UPLOAD_SUCCESS');
          logToken('STT_SUCCESS', { text: response.transcription.text });
          logToken('QUERY_SUCCESS', { intent: response.query_response.intent });

          if (response.transcription.text) {
            setTranscript(response.transcription.text);
            onTranscriptChange?.(response.transcription.text);
          }

          setState('RESPONSE');
          onResult?.(response);

          // If TTS audio is returned, play it
          if (response.audio_base64) {
            logToken('TTS_STARTED');
            logToken('TTS_SUCCESS');
            setState('PLAYING_AUDIO');
            logToken('PLAYBACK_STARTED');

            currentAudioElementRef.current = voiceService.playBase64(response.audio_base64, 'audio/wav', {
              onEnded: () => {
                setState('COMPLETED');
              },
              onError: (e) => {
                console.warn('TTS playback error:', e);
                setState('COMPLETED');
              },
            });
          } else {
            setState('COMPLETED');
          }
        } catch (err: any) {
          console.error('Voice processing error:', err);
          setState('ERROR');
          const msg = err.message || 'Failed to process voice query.';
          setErrorMessage(msg);
          onError?.(msg);
        } finally {
          cleanupMedia();
          resolve();
        }
      };

      try {
        recorder.stop();
      } catch (e) {
        console.warn('Error stopping recorder:', e);
        cleanupMedia();
        resolve();
      }
    });
  }, [language, cleanupMedia, onError, onResult, onTranscriptChange]);

  const cancelRecording = useCallback(() => {
    cleanupMedia();
    setState('IDLE');
    setTranscript('');
    setErrorMessage(null);
  }, [cleanupMedia]);

  return {
    state,
    transcript,
    errorMessage,
    audioLevel,
    isPermissionGranted,
    startRecording,
    stopRecordingAndProcess,
    cancelRecording,
    setTranscript,
  };
}
