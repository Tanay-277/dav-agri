import { apiRequest } from './apiClient';
import { LanguageCode, QueryResponse } from '../types';

export interface TranscribeResult {
  text: string;
  confidence: number;
  language: string;
}

export interface VoiceQueryResult {
  transcription: TranscribeResult;
  query_response: QueryResponse;
  audio_base64?: string;
}

export interface VoiceSampleResult {
  language: string;
  sample_text: string;
  audio_base64: string;
  mime_type?: string;
}

// Track active audio instance to prevent overlapping audio
let activeAudioElement: HTMLAudioElement | null = null;

export const voiceService = {
  stopActiveAudio() {
    if (activeAudioElement) {
      try {
        activeAudioElement.pause();
        activeAudioElement.currentTime = 0;
      } catch (_) {}
      activeAudioElement = null;
    }
  },

  async transcribeAudio(audioBlob: Blob, language: LanguageCode = 'mr'): Promise<TranscribeResult> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.wav');
    formData.append('language', language);

    return apiRequest<TranscribeResult>('/voice/transcribe', {
      method: 'POST',
      body: formData,
    });
  },

  async sendVoiceQuery(audioBlob: Blob, language: LanguageCode = 'mr', synthesize: boolean = true): Promise<VoiceQueryResult> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'voice_query.wav');
    formData.append('language', language);
    formData.append('synthesize_response', synthesize ? 'true' : 'false');

    return apiRequest<VoiceQueryResult>('/voice/query', {
      method: 'POST',
      body: formData,
    });
  },

  async synthesizeSpeech(text: string, language: LanguageCode = 'mr'): Promise<Blob> {
    console.log(`[TTS_REQUEST_STARTED] language=${language} text_length=${text.length}`);
    const res = await apiRequest<Blob>('/voice/synthesize', {
      method: 'POST',
      body: JSON.stringify({ text, language }),
    });
    console.log(`[TTS_RESPONSE_RECEIVED] content_type=${res.type || 'audio/mpeg'}`);
    return res;
  },

  async getSample(language: LanguageCode = 'mr'): Promise<VoiceSampleResult> {
    console.log(`[TTS_REQUEST_STARTED] language=${language}`);
    const res = await apiRequest<VoiceSampleResult>(`/voice/sample?language=${language}`);
    console.log(`[TTS_RESPONSE_RECEIVED] language=${res.language} bytes=${res.audio_base64?.length}`);
    return res;
  },

  playAudioBlob(
    blob: Blob,
    callbacks?: { onPlay?: () => void; onEnded?: () => void; onError?: (err: any) => void }
  ): HTMLAudioElement {
    this.stopActiveAudio();

    console.log('[AUDIO_LOAD_STARTED]', { size: blob.size, type: blob.type });
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    activeAudioElement = audio;

    audio.onplay = () => {
      console.log('[AUDIO_PLAY_STARTED]');
      callbacks?.onPlay?.();
    };

    audio.onended = () => {
      console.log('[AUDIO_PLAY_ENDED]');
      URL.revokeObjectURL(url);
      if (activeAudioElement === audio) {
        activeAudioElement = null;
      }
      callbacks?.onEnded?.();
    };

    audio.onerror = (e) => {
      console.error('[AUDIO_ERROR]', e);
      URL.revokeObjectURL(url);
      if (activeAudioElement === audio) {
        activeAudioElement = null;
      }
      callbacks?.onError?.(e);
    };

    audio.play().catch((err) => {
      console.error('[AUDIO_PLAY_FAILED]', err);
      URL.revokeObjectURL(url);
      if (activeAudioElement === audio) {
        activeAudioElement = null;
      }
      callbacks?.onError?.(err);
    });

    return audio;
  },

  playBase64(
    base64Data: string,
    mimeType: string = 'audio/mpeg',
    callbacks?: { onPlay?: () => void; onEnded?: () => void; onError?: (err: any) => void }
  ): HTMLAudioElement {
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);

    // Auto-detect audio container format from header magic bytes
    let detectedMime = mimeType;
    if (byteArray.length >= 3 && byteArray[0] === 0x49 && byteArray[1] === 0x44 && byteArray[2] === 0x33) {
      detectedMime = 'audio/mpeg'; // ID3 MP3
    } else if (byteArray.length >= 2 && byteArray[0] === 0xff && (byteArray[1] === 0xfb || byteArray[1] === 0xf3 || byteArray[1] === 0xf2)) {
      detectedMime = 'audio/mpeg'; // MP3 frame sync
    } else if (byteArray.length >= 4 && byteArray[0] === 0x52 && byteArray[1] === 0x49 && byteArray[2] === 0x46 && byteArray[3] === 0x46) {
      detectedMime = 'audio/wav'; // WAV RIFF
    }

    const blob = new Blob([byteArray], { type: detectedMime });
    return this.playAudioBlob(blob, callbacks);
  },
};
