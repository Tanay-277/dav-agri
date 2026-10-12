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
  /**
   * True until the stored session has been checked against the backend. The
   * launch screen waits for this so a signed-in farmer is never briefly shown
   * the sign-up screen while their profile is still loading.
   */
  isRestoring: boolean;
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
  isRestoring: authService.hasToken(),
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
    // Authenticated areas must never land back on sign-up. `previousScreen` is
    // a single slot that any navigation overwrites, so a guard is the only
    // reliable way to keep a signed-in farmer out of the onboarding screens.
    const authScreens: ScreenId[] = ['login', 'register'];
    const target = state.previousScreen;

    if (target && !authScreens.includes(target)) {
      state.previousScreen = undefined;
      state.currentScreen = target;
    } else {
      state.previousScreen = undefined;
      state.currentScreen = state.user?.onboarding_completed ? 'home' : 'login';
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
    state.isRestoring = false;
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
    // Always resolve, including when there is no token, so the launch screen
    // never waits forever on a session that cannot exist.
    if (!authService.hasToken()) {
      state.isRestoring = false;
      state.user = null;
      state.profile = null;
      emitChange();
      return;
    }

    try {
      const user = await authService.getCurrentUser();
      store.setUser(user);
      const profile = await profileService.getProfile();
      store.setProfile(profile);
    } catch (err) {
      // An expired or rejected token must clear the session, or every later
      // request would keep failing while the UI showed a signed-in user.
      authService.logout();
      store.setUser(null);
      store.setProfile(null);
    } finally {
      state.isRestoring = false;
      emitChange();
    }
  },

  /**
   * The single place that decides where a user goes after authenticating.
   *
   * Both sign-in paths (Google and username/password) must agree, otherwise a returning
   * farmer is sent back through language selection and voice setup every time
   * they open the app. A user who finished onboarding goes straight to the
   * dashboard; a new user continues at language selection.
   */
  routeAfterAuth(user: Pick<User, 'onboarding_completed'> | null) {
    if (!user) {
      store.setScreen('login');
      return;
    }
    store.setScreen(user.onboarding_completed ? 'home' : 'lang_select');
  },

  /**
   * Resolve the entry screen from the current session.
   *
   * Used by the launch screen once the session has been restored, so reloading
   * the app does not throw a signed-in farmer back to the sign-up options.
   */
  resolveEntryScreen(): ScreenId {
    if (!authService.hasToken() || !state.user) {
      return 'login';
    }
    return state.user.onboarding_completed ? 'home' : 'lang_select';
  },

  proceedFromLaunch() {
    store.setScreen(store.resolveEntryScreen());
  },

  subscribe(listener: Listener) {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  },
};

// A rejected token is reported by apiClient as a session-expired event. The app
// must respond by clearing the session and returning to sign-in, otherwise the
// user is left on an authenticated screen that cannot make a single request.
if (typeof window !== 'undefined') {
  window.addEventListener('dav:session-expired', () => {
    state.user = null;
    state.profile = null;
    state.processedResult = null;
    state.isRestoring = false;
    state.previousScreen = undefined;
    state.currentScreen = 'login';
    emitChange();
  });
}

export function useStore(): [AppState, typeof store] {
  const [snapshot, setSnapshot] = useState(store.getState());

  useEffect(() => {
    return store.subscribe(() => {
      setSnapshot({ ...store.getState() });
    });
  }, []);

  return [snapshot, store];
}
