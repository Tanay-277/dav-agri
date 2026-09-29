import React, { useEffect, useState } from 'react';
import { Sprout, Grid, Mic, Keyboard, ChevronRight } from 'lucide-react';
import { TopBar } from '../components/common/TopBar';
import { BottomNav } from '../components/common/BottomNav';
import { MultiLineChart } from '../components/charts/MultiLineChart';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { farmService } from '../services/farmService';
import { queryService } from '../services/queryService';
import { ConversationHistoryItem } from '../types';

export const FarmScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [activeTab, setActiveTab] = useState<'production' | 'land'>('production');
  const [conversations, setConversations] = useState<ConversationHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    farmService
      .getConversations(5)
      .then((data) => {
        if (isMounted) setConversations(data);
      })
      .catch(console.warn)
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const handleConversationClick = async (conv: ConversationHistoryItem) => {
    try {
      const res = await queryService.executeQuery(conv.query_text, state.language);
      store.setProcessedResult(res);
      store.setScreen('processed');
    } catch (err) {
      store.setScreen('processed');
    }
  };

  return (
    <div className="w-full min-h-screen bg-[#e8e5df] flex flex-col justify-between pb-28 select-none">
      {/* Top Bar */}
      <TopBar />

      <div className="flex-1 px-6 max-w-md mx-auto w-full flex flex-col gap-5 overflow-y-auto pt-1">
        {/* Top Toggle Pills: उत्पादन & माझी जमीन */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('production')}
            className={`py-2.5 px-5 rounded-full flex items-center gap-2 text-xs font-semibold shadow-sm transition-all active:scale-95 ${
              activeTab === 'production'
                ? 'bg-white text-stone-900 border border-stone-200'
                : 'bg-stone-300/60 text-stone-700 hover:bg-stone-300'
            }`}
          >
            <Sprout size={16} />
            <span>{t.production}</span>
          </button>

          <button
            onClick={() => setActiveTab('land')}
            className={`py-2.5 px-5 rounded-full flex items-center gap-2 text-xs font-semibold shadow-sm transition-all active:scale-95 ${
              activeTab === 'land'
                ? 'bg-white text-stone-900 border border-stone-200'
                : 'bg-stone-300/60 text-stone-700 hover:bg-stone-300'
            }`}
          >
            <Grid size={16} />
            <span>{t.my_land}</span>
          </button>
        </div>

        {/* Section: माझे संवाद (My Conversations) */}
        <div>
          <div className="flex items-center justify-between mb-3 px-1">
            <span className="text-stone-900 font-bold text-sm tracking-tight">
              {t.my_conversations}
            </span>
            <button
              onClick={() => store.setScreen('farm_topic')}
              className="text-stone-600 text-xs font-semibold hover:text-stone-900"
            >
              {t.view_all}
            </button>
          </div>

          <div className="flex flex-col gap-2.5">
            {conversations.length > 0 ? (
              conversations.map((conv, idx) => (
                <div
                  key={conv.id || idx}
                  onClick={() => handleConversationClick(conv)}
                  className="bg-white/90 hover:bg-white rounded-2xl py-3 px-4 flex items-center justify-between border border-stone-200 shadow-sm cursor-pointer active:scale-98 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-full bg-stone-100 flex items-center justify-center text-stone-700">
                      {idx % 2 === 0 ? <Mic size={15} /> : <Keyboard size={15} />}
                    </div>
                    <span className="text-xs font-medium text-stone-900 truncate max-w-[220px]">
                      {conv.query_text}
                    </span>
                  </div>
                  <ChevronRight size={16} className="text-stone-400" />
                </div>
              ))
            ) : (
              // Fallback default conversation items matching Figma Screen 13
              <>
                <div
                  onClick={() => store.setScreen('farm_topic')}
                  className="bg-white/90 hover:bg-white rounded-2xl py-3 px-4 flex items-center justify-between border border-stone-200 shadow-sm cursor-pointer active:scale-98 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <Mic size={16} className="text-stone-700" />
                    <span className="text-xs font-medium text-stone-900">
                      {t.cotton_income_title}
                    </span>
                  </div>
                  <ChevronRight size={16} className="text-stone-400" />
                </div>

                <div
                  onClick={() => store.setScreen('farm_topic')}
                  className="bg-white/90 hover:bg-white rounded-2xl py-3 px-4 flex items-center justify-between border border-stone-200 shadow-sm cursor-pointer active:scale-98 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <Mic size={16} className="text-stone-700" />
                    <span className="text-xs font-medium text-stone-900">
                      {t.total_farm_expenses}
                    </span>
                  </div>
                  <ChevronRight size={16} className="text-stone-400" />
                </div>
              </>
            )}
          </div>
        </div>

        {/* Section: माझी जमीन (My Land) Chart */}
        <div>
          <div className="flex items-center justify-between mb-3 px-1">
            <span className="text-stone-900 font-bold text-sm tracking-tight">
              {t.my_land}
            </span>
            <button
              onClick={() => store.setScreen('farm_topic')}
              className="text-stone-600 text-xs font-semibold hover:text-stone-900"
            >
              {t.view_all}
            </button>
          </div>

          <div onClick={() => store.setScreen('farm_topic')} className="cursor-pointer">
            <MultiLineChart title={t.multi_crop_income_title} />
          </div>
        </div>
      </div>

      {/* Persistent Bottom Nav */}
      <BottomNav activeScreen="farm" />
    </div>
  );
};
