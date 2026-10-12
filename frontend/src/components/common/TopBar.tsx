import React from 'react';
import { ChevronLeft } from 'lucide-react';
import { LanguageButton } from './LanguageButton';
import { useStore } from '../../state/store';

import { getTranslation } from '../../i18n';

interface TopBarProps {
  title?: string;
  showBack?: boolean;
  backText?: string;
  onBack?: () => void;
  showLanguagePill?: boolean;
  /** Match the surrounding screen's palette. */
  languageVariant?: 'light' | 'dark';
  className?: string;
}

export const TopBar: React.FC<TopBarProps> = ({
  title,
  showBack = false,
  backText,
  onBack,
  showLanguagePill = true,
  languageVariant = 'light',
  className = '',
}) => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);

  return (
    <div className={`w-full flex items-center justify-between px-6 pt-5 pb-3 select-none ${className}`}>
      {/* Left: Back button. A spacer of the same size is used when there is no
          back action, so the centred title and the language control do not
          shift sideways between screens. */}
      {showBack ? (
        <button
          type="button"
          onClick={onBack || (() => store.goBack())}
          aria-label={backText !== undefined ? backText : t.back}
          className="flex items-center gap-1.5 text-stone-800 hover:text-stone-900 active:scale-95 transition-transform"
        >
          <div className="w-9 h-9 rounded-full bg-stone-300/80 flex items-center justify-center shadow-sm">
            <ChevronLeft size={22} className="text-stone-700" />
          </div>
          <span className="text-stone-800 font-medium text-sm">{backText !== undefined ? backText : t.back}</span>
        </button>
      ) : (
        <div className="w-9 h-9" aria-hidden="true" />
      )}

      {/* Center: Title */}
      {title && (
        <h1 className="text-base font-semibold text-stone-800 tracking-tight">
          {title}
        </h1>
      )}

      {/* Right: Language switcher. This used to cycle silently through the
          three languages on every tap. It now opens the same explicit picker
          used on the launch and sign-in screens, so the chosen language is
          visible before it is applied. */}
      {showLanguagePill ? (
        <LanguageButton variant={languageVariant} />
      ) : (
        <div className="w-9 h-9" aria-hidden="true" />
      )}
    </div>
  );
};
