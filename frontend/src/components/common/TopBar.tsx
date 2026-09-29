import React from 'react';
import { Menu, ChevronLeft } from 'lucide-react';
import { useStore } from '../../state/store';
import { LanguageCode } from '../../types';

import { getTranslation } from '../../i18n';

interface TopBarProps {
  title?: string;
  showBack?: boolean;
  backText?: string;
  onBack?: () => void;
  showLanguagePill?: boolean;
  className?: string;
}

export const TopBar: React.FC<TopBarProps> = ({
  title,
  showBack = false,
  backText,
  onBack,
  showLanguagePill = true,
  className = '',
}) => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);

  const cycleLanguage = () => {
    const langs: LanguageCode[] = ['mr', 'hi', 'en'];
    const nextIdx = (langs.indexOf(state.language) + 1) % langs.length;
    store.setLanguage(langs[nextIdx]);
  };

  const getLangPillLabel = () => {
    if (state.language === 'en') return 'EN';
    if (state.language === 'hi') return 'हि';
    return 'अ';
  };

  return (
    <div className={`w-full flex items-center justify-between px-6 pt-5 pb-3 select-none ${className}`}>
      {/* Left: Back button or Hamburger menu */}
      {showBack ? (
        <button
          onClick={onBack || (() => store.goBack())}
          className="flex items-center gap-1.5 text-stone-800 hover:text-stone-900 active:scale-95 transition-transform"
        >
          <div className="w-9 h-9 rounded-full bg-stone-300/80 flex items-center justify-center shadow-sm">
            <ChevronLeft size={22} className="text-stone-700" />
          </div>
          <span className="text-stone-800 font-medium text-sm">{backText !== undefined ? backText : t.back}</span>
        </button>
      ) : (
        <button
          onClick={() => {}}
          className="w-9 h-9 rounded-full flex flex-col justify-center items-center gap-1 hover:bg-stone-300/50 transition-colors"
        >
          <div className="w-5 h-0.5 bg-stone-800 rounded-full"></div>
          <div className="w-5 h-0.5 bg-stone-800 rounded-full"></div>
        </button>
      )}

      {/* Center: Title */}
      {title && (
        <h1 className="text-base font-semibold text-stone-800 tracking-tight">
          {title}
        </h1>
      )}

      {/* Right: Language Switcher Pill */}
      {showLanguagePill ? (
        <button
          onClick={cycleLanguage}
          title="Change Language"
          className="w-9 h-9 rounded-full bg-stone-300/80 hover:bg-stone-400/80 text-stone-800 font-semibold text-sm flex items-center justify-center shadow-sm active:scale-95 transition-all"
        >
          {getLangPillLabel()}
        </button>
      ) : (
        <div className="w-9 h-9" />
      )}
    </div>
  );
};
