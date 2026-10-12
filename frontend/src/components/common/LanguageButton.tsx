import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { Check, Globe } from 'lucide-react';
import { useStore } from '../../state/store';
import { LanguageCode } from '../../types';
import { getTranslation } from '../../i18n';

const LANGUAGES: { code: LanguageCode; label: string; script: string }[] = [
  { code: 'en', label: 'English', script: 'ABC' },
  { code: 'hi', label: 'हिन्दी', script: 'कखग' },
  { code: 'mr', label: 'मराठी', script: 'कखग' },
];

/** Short label shown on the collapsed pill. */
const PILL_LABEL: Record<LanguageCode, string> = {
  en: 'EN',
  hi: 'हि',
  mr: 'अ',
};

interface LanguageButtonProps {
  /** Match the surrounding screen's palette. */
  variant?: 'light' | 'dark';
  className?: string;
}

/**
 * Language configuration button.
 *
 * Language used to be reachable only by tapping "Continue with Google", which
 * made it look like the two were the same control. It is an independent
 * preference and is now available on the launch and sign-in screens directly.
 *
 * The sheet is rendered through a portal on document.body. It is absolutely
 * positioned, and the button is often nested inside a small wrapper, so without
 * the portal it resolved its containing block against that wrapper and rendered
 * off-screen at a fraction of the expected width.
 */
export const LanguageButton: React.FC<LanguageButtonProps> = ({
  variant = 'light',
  className = '',
}) => {
  const [state, store] = useStore();
  const [open, setOpen] = useState(false);
  const t = getTranslation(state.language);

  const isDark = variant === 'dark';

  // Close on Escape so the dialog is keyboard-dismissible.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open]);

  const pill = isDark
    ? 'bg-white/15 text-white border border-white/25'
    : 'bg-stone-300/80 text-stone-800 border border-transparent';

  const sheet = isDark
    ? 'bg-stone-900 text-white border-white/15'
    : 'bg-white text-stone-900 border-stone-200';

  const optionIdle = isDark
    ? 'text-stone-200 hover:bg-white/10'
    : 'text-stone-700 hover:bg-stone-100';
  const optionActive = isDark
    ? 'bg-white/15 text-white'
    : 'bg-stone-200 text-stone-900';

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label={t.language}
        aria-haspopup="dialog"
        className={`flex items-center gap-1.5 rounded-full px-3 h-9 font-semibold text-sm shadow-sm active:scale-95 transition-all ${pill} ${className}`}
      >
        <Globe size={15} className="shrink-0" />
        <span>{PILL_LABEL[state.language]}</span>
      </button>

      {open &&
        createPortal(
          <div
            className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-[2px] flex items-center justify-center p-5"
            onClick={() => setOpen(false)}
            role="dialog"
            aria-modal="true"
            aria-label={t.language}
          >
            <div
              className={`w-full max-w-sm rounded-3xl p-5 shadow-2xl flex flex-col gap-2.5 border ${sheet}`}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-sm font-bold px-1 pb-1">{t.language}</h3>

              {LANGUAGES.map((lang) => {
                const isSelected = state.language === lang.code;
                return (
                  <button
                    key={lang.code}
                    type="button"
                    onClick={() => {
                      store.setLanguage(lang.code);
                      setOpen(false);
                    }}
                    aria-pressed={isSelected}
                    className={`w-full min-h-[52px] py-3 px-4 rounded-2xl flex items-center justify-between gap-3 font-medium text-sm transition-colors ${
                      isSelected ? optionActive : optionIdle
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
    </>
  );
};
