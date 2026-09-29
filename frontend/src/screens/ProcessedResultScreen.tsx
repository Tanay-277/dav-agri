import React, { useState } from 'react';
import { Volume2, Share2, Mic, Send, Check } from 'lucide-react';
import { TopBar } from '../components/common/TopBar';
import { StackedBarChart } from '../components/charts/StackedBarChart';
import { DonutChart } from '../components/charts/DonutChart';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { voiceService } from '../services/voiceService';
import { queryService } from '../services/queryService';

export const ProcessedResultScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [shared, setShared] = useState(false);
  const [inputText, setInputText] = useState('');
  const [sending, setSending] = useState(false);

  const result = state.processedResult;

  const defaultQueryText =
    state.language === 'en'
      ? 'My cotton production was 12 quintals in 2022, 15 in 2023, 18 in 2024, and 21 in 2025. Show me how my production has changed over the years.'
      : state.language === 'hi'
      ? 'मेरी कपास उत्पादन 2022 में 12 क्विंटल, 2023 में 15, 2024 में 18 और 2025 में 21 थी। उत्पादन में बदलाव समझाएं।'
      : 'माझ्या कापूस उत्पादनाची माहिती आणि खर्चाचा तक्ता समजावून सांगा.';

  const defaultExplanation =
    state.language === 'en'
      ? 'You produced 9 more quintals in 2025 than in 2022, which is a 75% increase in production. The highest jump was recorded between 2023 and 2024 with sustained irrigation.'
      : state.language === 'hi'
      ? 'आपने 2022 की तुलना में 2025 में 9 क्विंटल अधिक उत्पादन किया है, जो 75% की वृद्धि दर्शाता है। सर्वाधिक वृद्धि 2023 और 2024 के बीच दर्ज की गई।'
      : 'तुम्ही 2022 च्या तुलनेत 2025 मध्ये 9 क्विंटल अधिक उत्पादन घेतले आहे, जी 75% वाढ दर्शवते. सर्वाधिक वाढ 2023 ते 2024 दरम्यान झाली आहे.';

  const queryText = result?.query || defaultQueryText;
  const explanationText = result?.answer || defaultExplanation;

  const handleSpeakOut = async () => {
    if (isPlayingAudio) {
      voiceService.stopActiveAudio();
      setIsPlayingAudio(false);
      return;
    }
    setIsPlayingAudio(true);
    try {
      const audioBlob = await voiceService.synthesizeSpeech(explanationText, state.language);
      voiceService.playAudioBlob(audioBlob, {
        onEnded: () => setIsPlayingAudio(false),
        onError: () => setIsPlayingAudio(false),
      });
    } catch (err) {
      console.error('Speak out error:', err);
      setIsPlayingAudio(false);
    }
  };

  const handleShare = () => {
    setShared(true);
    if (navigator.clipboard) {
      const shareUrl = `${window.location.origin}/#share=${result?.share_token || 'demo'}`;
      navigator.clipboard.writeText(shareUrl).catch(() => {});
    }
    setTimeout(() => setShared(false), 2500);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    setSending(true);
    try {
      const res = await queryService.executeQuery(inputText.trim(), state.language);
      store.setProcessedResult(res);
      setInputText('');
    } catch (err) {
      console.warn('Query failed:', err);
    } finally {
      setSending(false);
    }
  };

  const isDonut = result?.visualization?.type === 'donut';

  return (
    <div className="w-full min-h-screen bg-[#e8e5df] flex flex-col justify-between pb-4 select-none">
      {/* Top Bar with Back Arrow */}
      <TopBar showBack={true} onBack={() => store.setScreen('home')} />

      <div className="flex-1 px-6 max-w-md mx-auto w-full flex flex-col gap-4 overflow-y-auto pt-1 pb-2">
        {/* User Query Bubble (Right-aligned) */}
        <div className="flex justify-end">
          <div className="bg-white rounded-2xl rounded-tr-sm p-4 max-w-[85%] shadow-sm border border-stone-200/80">
            <p className="text-xs font-semibold text-stone-900 leading-relaxed">
              {queryText}
            </p>
          </div>
        </div>

        {/* Structured Chart Card */}
        <div>
          {isDonut ? (
            <DonutChart />
          ) : (
            <StackedBarChart
              data={result?.visualization}
              title={result?.visualization?.title || (state.language === 'en' ? 'Cotton Production' : state.language === 'hi' ? 'कपास उत्पादन' : 'कापूस उत्पादन')}
            />
          )}
        </div>

        {/* Action Pills: Speak Out & Share */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={handleSpeakOut}
            className={`py-3 px-4 rounded-full bg-white border border-stone-200 shadow-sm text-stone-900 font-semibold text-xs flex items-center justify-center gap-2 active:scale-96 transition-all ${
              isPlayingAudio ? 'ring-2 ring-blue-500' : ''
            }`}
          >
            <Volume2 size={16} className={isPlayingAudio ? 'animate-pulse text-blue-600' : ''} />
            <span>{t.speak_out}</span>
          </button>

          <button
            onClick={handleShare}
            className="py-3 px-4 rounded-full bg-white border border-stone-200 shadow-sm text-stone-900 font-semibold text-xs flex items-center justify-center gap-2 active:scale-96 transition-all"
          >
            {shared ? (
              <>
                <Check size={16} className="text-green-600" />
                <span>{t.link_copied}</span>
              </>
            ) : (
              <>
                <Share2 size={16} />
                <span>{t.share}</span>
              </>
            )}
          </button>
        </div>

        {/* Explanation Card */}
        <div className="bg-white/80 rounded-3xl p-5 border border-stone-200/80 shadow-sm">
          <h4 className="text-stone-900 font-bold text-xs uppercase tracking-wider mb-2">
            {t.explanation}
          </h4>
          <p className="text-stone-800 text-xs font-medium leading-relaxed">
            {explanationText}
          </p>
        </div>
      </div>

      {/* Bottom Message Input Bar */}
      <div className="px-6 max-w-md mx-auto w-full pt-2">
        <form onSubmit={handleSendMessage} className="flex items-center gap-2">
          <div className="flex-1 bg-white rounded-full px-4 py-2.5 flex items-center border border-stone-300 shadow-sm">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={t.type_message}
              className="w-full text-xs text-stone-900 placeholder-stone-500 focus:outline-none bg-transparent"
            />
            {inputText.trim() && (
              <button type="submit" disabled={sending} className="ml-2 text-stone-800">
                <Send size={15} />
              </button>
            )}
          </div>

          <button
            type="button"
            onClick={() => store.setScreen('listening')}
            className="w-11 h-11 rounded-full bg-white border border-stone-300 flex items-center justify-center shadow-sm text-stone-900 active:scale-95 transition-transform"
          >
            <Mic size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};
