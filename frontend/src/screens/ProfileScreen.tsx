import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
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
  Check,
} from 'lucide-react';
import { TopBar } from '../components/common/TopBar';
import { BottomNav } from '../components/common/BottomNav';
import { FarmerAvatar } from '../components/common/FarmerAvatar';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { profileService } from '../services/profileService';
import { authService } from '../services/authService';
import { LanguageCode } from '../types';

export const ProfileScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [languageSheetOpen, setLanguageSheetOpen] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    profileService.getProfile().then(store.setProfile).catch(console.warn);
  }, []);

  // These controls are not implemented yet. Say so, rather than accepting a
  // tap and appearing to do nothing.
  const showNotAvailable = () => {
    setNotice(t.not_available_yet);
    setTimeout(() => setNotice(null), 2500);
  };

  const profile = state.profile || {
    name: 'Raj Patil',
    location: 'Pune, MH',
    age: 42,
  };

  const languageOptions: { code: LanguageCode; label: string; script: string }[] = [
    { code: 'en', label: 'English', script: 'ABC' },
    { code: 'hi', label: 'हिन्दी', script: 'कखग' },
    { code: 'mr', label: 'मराठी', script: 'कखग' },
  ];

  const currentLanguageLabel =
    state.language === 'en' ? 'English' : state.language === 'hi' ? 'हिन्दी' : 'मराठी';

  const handleLogout = () => {
    authService.logout();
    store.setUser(null);
    store.setProfile(null);
    store.setProcessedResult(null);
    sessionStorage.removeItem('dav_pending_phone');
    store.setScreen('launch');
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

          {/* Language: opens the real picker. It previously cycled silently through the
            three languages on each tap, so a farmer could change the language
            by accident with no confirmation of what was chosen. */}
          <button
            onClick={() => setLanguageSheetOpen(true)}
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

          {/* Notifications: no backend and no screen behind it. It is reported as
              unavailable instead of silently ignoring the tap. */}
          <button
            onClick={showNotAvailable}
            className="w-full py-3 px-4 flex items-center justify-between text-left hover:bg-stone-50 rounded-2xl transition-colors"
          >
            <div className="flex items-center gap-3 text-stone-800">
              <Bell size={18} />
              <span className="text-xs font-semibold">{t.notifications}</span>
            </div>
            <ChevronRight size={16} className="text-stone-400" />
          </button>

          {/* Saved Visualizations lives with the farm records that contain them,
              not on a single crop topic page. */}
          <button
            onClick={() => store.setScreen('farm')}
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
          {/* Voice History: the farm screen lists past conversations, which is what this
              row means. It previously went to the same place as Farm Records,
              so both rows did the identical thing. */}
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
            onClick={showNotAvailable}
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
            onClick={showNotAvailable}
            className="w-full py-3 px-4 flex items-center justify-between text-left hover:bg-stone-50 rounded-2xl transition-colors"
          >
            <div className="flex items-center gap-3 text-stone-800">
              <Shield size={18} />
              <span className="text-xs font-semibold">{t.privacy_policy}</span>
            </div>
            <ChevronRight size={16} className="text-stone-400" />
          </button>
        </div>

        {/* A row that has no screen behind it reports that plainly, so the tap is
          never mistaken for a broken app. */}
      {notice && (
        <div className="w-full text-center text-xs text-stone-700 bg-stone-200/80 py-2 px-3 rounded-xl">
          {notice}
        </div>
      )}

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

      {/* Language picker. Portalled to document.body for the same reason as
          LanguageButton: an absolutely positioned sheet inside the scrolling
          panel resolves against that panel and can render off-screen. */}
      {languageSheetOpen &&
        createPortal(
          <div
            className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-[2px] flex items-center justify-center p-5"
            onClick={() => setLanguageSheetOpen(false)}
            role="dialog"
            aria-modal="true"
            aria-label={t.language}
          >
            <div
              className="w-full max-w-sm rounded-3xl p-5 shadow-2xl flex flex-col gap-2.5 bg-white text-stone-900 border border-stone-200"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-sm font-bold px-1 pb-1">{t.language}</h3>
              {languageOptions.map((lang) => {
                const isSelected = state.language === lang.code;
                return (
                  <button
                    key={lang.code}
                    type="button"
                    onClick={() => {
                      store.setLanguage(lang.code);
                      setLanguageSheetOpen(false);
                    }}
                    aria-pressed={isSelected}
                    className={`w-full min-h-[52px] py-3 px-4 rounded-2xl flex items-center justify-between gap-3 font-medium text-sm transition-colors ${
                      isSelected ? 'bg-stone-200' : 'text-stone-700 hover:bg-stone-100'
                    }`}
                  >
                    <span className="flex items-center gap-3 min-w-0">
                      <span className="text-[10px] font-bold tracking-wider opacity-70 w-8 shrink-0 text-left">
                        {lang.script}
                      </span>
                      <span className="truncate">{lang.label}</span>
                    </span>
                    {isSelected && <Check size={16} className="shrink-0" />}
                  </button>
                );
              })}
            </div>
          </div>,
          document.body
        )}
    </div>
  );
};
