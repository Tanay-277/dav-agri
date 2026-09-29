import { useState, useEffect } from 'react';
import { ScreenId, LanguageCode, User, Profile, QueryResult } from '../types';
import { authService } from '../services/authService';
import { profileService } from '../services/profileService';
import { onboardingService } from '../services/onboardingService';

type Listener = () => void;

interface AppState {
  currentScreen: ScreenId;
  previousScreen?: ScreenId;
  language: LanguageCode;
  user: User | null;
  profile: Profile | null;
  processedResult: QueryResult | null;
  selectedCropId: string;
  isRecording: boolean;
  activeTopicModal: boolean;
}

// Authoritative Language State: Restore from localStorage if present
const storedLang = typeof window !== 'undefined' ? (localStorage.getItem('dav_language') as LanguageCode) : null;
const initialLanguage: LanguageCode = (storedLang === 'en' || storedLang === 'hi' || storedLang === 'mr') ? storedLang : 'en';

const state: AppState = {
  currentScreen: 'launch',
  language: initialLanguage,
  user: null,
  profile: null,
  processedResult: null,
  selectedCropId: 'crop_cotton',
  isRecording: false,
  activeTopicModal: false,
};

const listeners = new Set<Listener>();

function emitChange() {
  for (const listener of listeners) {
    listener();
  }
}

export const store = {
  getState(): AppState {
    return state;
  },

  setScreen(screen: ScreenId) {
    state.previousScreen = state.currentScreen;
    state.currentScreen = screen;
    emitChange();
  },

  goBack() {
    if (state.previousScreen) {
      const prev = state.previousScreen;
      state.previousScreen = undefined;
      state.currentScreen = prev;
    } else {
      state.currentScreen = 'home';
    }
    emitChange();
  },

  setLanguage(lang: LanguageCode) {
    state.language = lang;
    if (typeof window !== 'undefined') {
      localStorage.setItem('dav_language', lang);
    }
    // Synchronize to backend if session or user exists
    if (authService.hasToken()) {
      onboardingService.confirmLanguage(lang).catch((err) => {
        console.warn('Failed to sync language to backend user profile:', err);
      });
    }
    emitChange();
  },

  setUser(user: User | null) {
    state.user = user;
    if (user?.preferred_language && (user.preferred_language === 'en' || user.preferred_language === 'hi' || user.preferred_language === 'mr')) {
      state.language = user.preferred_language;
      if (typeof window !== 'undefined') {
        localStorage.setItem('dav_language', user.preferred_language);
      }
    }
    emitChange();
  },

  setProfile(profile: Profile | null) {
    state.profile = profile;
    emitChange();
  },

  setProcessedResult(res: QueryResult | null) {
    state.processedResult = res;
    emitChange();
  },

  setSelectedCrop(cropId: string) {
    state.selectedCropId = cropId;
    emitChange();
  },

  setRecording(recording: boolean) {
    state.isRecording = recording;
    emitChange();
  },

  setTopicModal(open: boolean) {
    state.activeTopicModal = open;
    emitChange();
  },

  async loadInitialData() {
    if (authService.hasToken()) {
      try {
        const user = await authService.getCurrentUser();
        store.setUser(user);
        const profile = await profileService.getProfile();
        store.setProfile(profile);
      } catch (err) {
        authService.logout();
        store.setUser(null);
        store.setProfile(null);
      }
    }
  },

  proceedFromLaunch() {
    store.setScreen('signup_options');
  },

  subscribe(listener: Listener) {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  },
};

export function useStore(): [AppState, typeof store] {
  const [snapshot, setSnapshot] = useState(store.getState());

  useEffect(() => {
    return store.subscribe(() => {
      setSnapshot({ ...store.getState() });
    });
  }, []);

  return [snapshot, store];
}
