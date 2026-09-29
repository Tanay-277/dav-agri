import React from 'react';
import { useStore } from './state/store';

// Import All 17 Figma Screens
import { LaunchScreen } from './screens/LaunchScreen';
import { SignupOptionsScreen } from './screens/SignupOptionsScreen';
import { PhoneScreen } from './screens/PhoneScreen';
import { OtpScreen } from './screens/OtpScreen';
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

  const renderScreen = () => {
    switch (state.currentScreen) {
      case 'launch':
        return <LaunchScreen />;
      case 'signup_options':
        return <SignupOptionsScreen />;
      case 'phone':
        return <PhoneScreen />;
      case 'otp':
        return <OtpScreen />;
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
