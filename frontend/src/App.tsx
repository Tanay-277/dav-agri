import React, { useEffect, useRef } from 'react';
import { useStore, store } from './state/store';

// Import All 17 Figma Screens
import { LaunchScreen } from './screens/LaunchScreen';
import { LoginScreen } from './screens/LoginScreen';
import { RegisterScreen } from './screens/RegisterScreen';
import { LangSelectScreen } from './screens/LangSelectScreen';
import { LanguageConfirmScreen } from './screens/LanguageConfirmScreen';
import { VoiceSetupScreen } from './screens/VoiceSetupScreen';
import { OnboardedScreen } from './screens/OnboardedScreen';
import { WeatherScreen } from './screens/WeatherScreen';
import { HomeScreen } from './screens/HomeScreen';
import { ListeningScreen } from './screens/ListeningScreen';
import { ProcessedResultScreen } from './screens/ProcessedResultScreen';
import { FarmScreen } from './screens/FarmScreen';
import { FarmTopicScreen } from './screens/FarmTopicScreen';
import { TopicExplanationModal } from './screens/TopicExplanationModal';
import { ProfileScreen } from './screens/ProfileScreen';
import { EditProfileScreen } from './screens/EditProfileScreen';

export const App: React.FC = () => {
  const [state] = useStore();

  const suppressHistoryPush = useRef(false);

  // Android and iOS browsers bind the hardware/browser back gesture to the
  // history stack. With `replaceState` and no entries of our own, that gesture
  // closed the PWA from any screen, so the in-app back control and the device
  // back button behaved completely differently. Each screen now pushes an entry
  // and the popstate handler moves through the app instead.
  useEffect(() => {
    if (suppressHistoryPush.current) {
      // A popstate already consumed an entry; push a fresh one in its place so
      // the stack length stays constant as the farmer walks back and forth.
      suppressHistoryPush.current = false;
      window.history.pushState({ davScreen: state.currentScreen }, '');
      return;
    }
    window.history.pushState({ davScreen: state.currentScreen }, '');
  }, [state.currentScreen]);

  useEffect(() => {
    const onPopState = () => {
      if (store.getState().currentScreen === 'launch') {
        // Nothing behind the splash; let the gesture leave the app.
        return;
      }
      suppressHistoryPush.current = true;
      store.goBack();
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const renderScreen = () => {
    switch (state.currentScreen) {
      case 'launch':
        return <LaunchScreen />;
      case 'login':
        return <LoginScreen />;
      case 'register':
        return <RegisterScreen />;
      case 'lang_select':
        return <LangSelectScreen />;
      case 'language_confirm':
        return <LanguageConfirmScreen />;
      case 'voice_setup':
        return <VoiceSetupScreen />;
      case 'onboarded':
        return <OnboardedScreen />;
      case 'weather':
        return <WeatherScreen />;
      case 'home':
        return <HomeScreen />;
      case 'listening':
        return <ListeningScreen />;
      case 'processed':
        return <ProcessedResultScreen />;
      case 'farm':
        return <FarmScreen />;
      case 'farm_topic':
        return <FarmTopicScreen />;
      case 'topic_explanation':
        return (
          <>
            <FarmTopicScreen />
            <TopicExplanationModal />
          </>
        );
      case 'profile':
        return <ProfileScreen />;
      case 'edit_profile':
        return <EditProfileScreen />;
      default:
        return <HomeScreen />;
    }
  };

  return (
    <div className="h-[100dvh] sm:h-auto sm:min-h-screen bg-stone-950 flex flex-col items-center justify-center sm:py-6 sm:px-4 overflow-hidden sm:overflow-auto">
      {/* Main Screen Shell (Responsive flex-1 on mobile, framed on tablet/desktop) */}
      <main className="w-full max-w-md flex-1 sm:flex-none sm:h-[844px] sm:max-h-[92vh] bg-[#e8e5df] sm:rounded-3xl sm:border sm:border-stone-800 shadow-2xl relative overflow-hidden flex flex-col">
        {renderScreen()}
      </main>
    </div>
  );
};

export default App;
