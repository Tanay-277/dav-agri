import React, { useEffect, useState } from 'react';
import {
  User,
  Globe,
  Bell,
  BarChart3,
  FileText,
  Mic,
  Briefcase,
  Shield,
  ChevronRight,
  LogOut,
} from 'lucide-react';
import { TopBar } from '../components/common/TopBar';
import { BottomNav } from '../components/common/BottomNav';
import { FarmerAvatar } from '../components/common/FarmerAvatar';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { profileService } from '../services/profileService';
import { authService } from '../services/authService';

export const ProfileScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    profileService.getProfile().then(store.setProfile).catch(console.warn);
  }, []);

  const profile = state.profile || {
    name: 'Raj Patil',
    location: 'Pune, MH',
    age: 42,
  };

  const currentLanguageLabel =
    state.language === 'en' ? 'English' : state.language === 'hi' ? 'हिन्दी' : 'मराठी';

  const handleLogout = () => {
    authService.logout();
    store.setUser(null);
    store.setProfile(null);
    store.setScreen('signup_options');
  };

  return (
    <div className="w-full min-h-screen bg-[#e8e5df] flex flex-col justify-between pb-28 select-none">
      {/* Top Bar */}
      <TopBar showLanguagePill={false} />

      <div className="flex-1 px-6 max-w-md mx-auto w-full flex flex-col items-center gap-5 overflow-y-auto pt-1">
        {/* Farmer Avatar & Info */}
        <div className="flex flex-col items-center gap-2 pt-2">
          <FarmerAvatar size={130} />
          <h2 className="text-xl font-bold text-stone-900 tracking-tight mt-1">
            {profile.name}
          </h2>
          <div className="flex items-center gap-3 text-stone-700 text-xs font-semibold">
            <span>{profile.location}</span>
            <span>{profile.age}</span>
          </div>
        </div>

        {/* Settings Group 1 */}
        <div className="w-full bg-white/90 rounded-3xl p-2 border border-stone-200/80 shadow-sm flex flex-col divide-y divide-stone-100">
          {/* Edit Profile */}
          <button
            onClick={() => store.setScreen('edit_profile')}
            className="w-full py-3 px-4 flex items-center justify-between text-left hover:bg-stone-50 rounded-2xl transition-colors"
          >
            <div className="flex items-center gap-3 text-stone-800">
              <User size={18} />
              <span className="text-xs font-semibold">{t.edit_profile}</span>
            </div>
            <ChevronRight size={16} className="text-stone-400" />
          </button>

          {/* Language */}
          <button
            onClick={() => {
              const langs = ['mr', 'hi', 'en'] as const;
              const next = langs[(langs.indexOf(state.language) + 1) % langs.length];
              store.setLanguage(next);
            }}
            className="w-full py-3 px-4 flex items-center justify-between text-left hover:bg-stone-50 rounded-2xl transition-colors"
          >
            <div className="flex items-center gap-3 text-stone-800">
              <Globe size={18} />
              <span className="text-xs font-semibold">{t.language}</span>
            </div>
            <div className="flex items-center gap-1.5 text-stone-500 text-xs font-medium">
              <span>{currentLanguageLabel}</span>
              <ChevronRight size={16} className="text-stone-400" />
            </div>
          </button>

          {/* Notifications */}
          <button
            onClick={() => {}}
            className="w-full py-3 px-4 flex items-center justify-between text-left hover:bg-stone-50 rounded-2xl transition-colors"
          >
            <div className="flex items-center gap-3 text-stone-800">
              <Bell size={18} />
              <span className="text-xs font-semibold">{t.notifications}</span>
            </div>
            <ChevronRight size={16} className="text-stone-400" />
          </button>

          {/* Saved Visualizations */}
          <button
            onClick={() => store.setScreen('farm_topic')}
            className="w-full py-3 px-4 flex items-center justify-between text-left hover:bg-stone-50 rounded-2xl transition-colors"
          >
            <div className="flex items-center gap-3 text-stone-800">
              <BarChart3 size={18} />
              <span className="text-xs font-semibold">{t.saved_visualizations}</span>
            </div>
            <ChevronRight size={16} className="text-stone-400" />
          </button>

          {/* Farm Records */}
          <button
            onClick={() => store.setScreen('farm')}
            className="w-full py-3 px-4 flex items-center justify-between text-left hover:bg-stone-50 rounded-2xl transition-colors"
          >
            <div className="flex items-center gap-3 text-stone-800">
              <FileText size={18} />
              <span className="text-xs font-semibold">{t.farm_records}</span>
            </div>
            <ChevronRight size={16} className="text-stone-400" />
          </button>
        </div>

        {/* Settings Group 2 */}
        <div className="w-full bg-white/90 rounded-3xl p-2 border border-stone-200/80 shadow-sm flex flex-col divide-y divide-stone-100">
          {/* Voice History */}
          <button
            onClick={() => store.setScreen('farm')}
            className="w-full py-3 px-4 flex items-center justify-between text-left hover:bg-stone-50 rounded-2xl transition-colors"
          >
            <div className="flex items-center gap-3 text-stone-800">
              <Mic size={18} />
              <span className="text-xs font-semibold">{t.voice_history}</span>
            </div>
            <ChevronRight size={16} className="text-stone-400" />
          </button>

          {/* Terms & Conditions */}
          <button
            onClick={() => {}}
            className="w-full py-3 px-4 flex items-center justify-between text-left hover:bg-stone-50 rounded-2xl transition-colors"
          >
            <div className="flex items-center gap-3 text-stone-800">
              <Briefcase size={18} />
              <span className="text-xs font-semibold">{t.terms_conditions}</span>
            </div>
            <ChevronRight size={16} className="text-stone-400" />
          </button>

          {/* Privacy Policy */}
          <button
            onClick={() => {}}
            className="w-full py-3 px-4 flex items-center justify-between text-left hover:bg-stone-50 rounded-2xl transition-colors"
          >
            <div className="flex items-center gap-3 text-stone-800">
              <Shield size={18} />
              <span className="text-xs font-semibold">{t.privacy_policy}</span>
            </div>
            <ChevronRight size={16} className="text-stone-400" />
          </button>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="w-full py-3 px-4 rounded-2xl bg-stone-300/60 hover:bg-stone-300 text-stone-800 text-xs font-semibold flex items-center justify-center gap-2 active:scale-98 transition-all"
        >
          <LogOut size={15} />
          <span>{t.logout}</span>
        </button>
      </div>

      {/* Persistent Bottom Nav */}
      <BottomNav activeScreen="profile" />
    </div>
  );
};
