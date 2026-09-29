import React from 'react';
import { Mic, Warehouse, User as UserIcon } from 'lucide-react';
import { useStore } from '../../state/store';
import { getTranslation } from '../../i18n';
import { ScreenId } from '../../types';

interface BottomNavProps {
  activeScreen?: ScreenId;
}

export const BottomNav: React.FC<BottomNavProps> = ({ activeScreen }) => {
  const [state, store] = useStore();
  const current = activeScreen || state.currentScreen;
  const t = getTranslation(state.language);

  const isHome = current === 'home' || current === 'weather';
  const isFarm = current === 'farm' || current === 'farm_topic' || current === 'topic_explanation';
  const isProfile = current === 'profile' || current === 'edit_profile';

  return (
    <div className="absolute bottom-4 left-0 right-0 max-w-md mx-auto px-6 pointer-events-none z-30">
      <div className="pointer-events-auto bg-[#d6d1c7]/95 backdrop-blur-md border border-white/40 rounded-full px-3 py-2 flex items-center justify-around shadow-float">
        {/* Tab 1: Home (घर) */}
        <button
          onClick={() => store.setScreen('home')}
          className={`flex flex-col items-center justify-center py-1 px-5 rounded-full transition-all duration-200 ${
            isHome
              ? 'bg-stone-800 text-stone-100 shadow-sm scale-102'
              : 'text-stone-700 hover:text-stone-900 active:scale-95'
          }`}
        >
          <Mic size={20} className={isHome ? 'text-stone-100' : 'text-stone-700'} />
          <span className="text-[11px] font-medium mt-0.5">{t.home_tab}</span>
        </button>

        {/* Tab 2: Farm (शेत) */}
        <button
          onClick={() => store.setScreen('farm')}
          className={`flex flex-col items-center justify-center py-1 px-5 rounded-full transition-all duration-200 ${
            isFarm
              ? 'bg-stone-800 text-stone-100 shadow-sm scale-102'
              : 'text-stone-700 hover:text-stone-900 active:scale-95'
          }`}
        >
          <Warehouse size={20} className={isFarm ? 'text-stone-100' : 'text-stone-700'} />
          <span className="text-[11px] font-medium mt-0.5">{t.farm_tab}</span>
        </button>

        {/* Tab 3: Me / Profile (मी) */}
        <button
          onClick={() => store.setScreen('profile')}
          className={`flex flex-col items-center justify-center py-1 px-5 rounded-full transition-all duration-200 ${
            isProfile
              ? 'bg-stone-800 text-stone-100 shadow-sm scale-102'
              : 'text-stone-700 hover:text-stone-900 active:scale-95'
          }`}
        >
          <UserIcon size={20} className={isProfile ? 'text-stone-100' : 'text-stone-700'} />
          <span className="text-[11px] font-medium mt-0.5">{t.me_tab}</span>
        </button>
      </div>
    </div>
  );
};
