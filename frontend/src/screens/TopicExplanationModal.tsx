import React, { useState } from 'react';
import { X, Volume2 } from 'lucide-react';
import { DonutChart } from '../components/charts/DonutChart';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { voiceService } from '../services/voiceService';

export const TopicExplanationModal: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [isPlaying, setIsPlaying] = useState(false);

  const explanationText =
    state.language === 'en'
      ? 'This chart illustrates the proportional breakdown of your total farm expenditure. Labor accounts for the highest single portion at 40%, followed by Seeds (25%), Fertilizer (20%), and Pesticides (15%).'
      : state.language === 'hi'
      ? 'इस पाई चार्ट में आपकी खेती के कुल खर्च का सटीक विभाजन दर्शाया गया है। मजदूरी पर सबसे अधिक 40% खर्च हुआ है। इसके बाद बीजों पर 25%, खाद पर 20% और कीटनाशकों पर 15% खर्च हुआ है।'
      : 'या पाई चार्टमध्ये तुमच्या शेतीसाठी केलेल्या एकूण खर्चाचे वेगवेगळे भाग दाखवले आहेत. प्रत्येक भाग एकूण खर्चातील किती टक्के आहे, हे यातून सहज समजते.\n\nमजुरीवर सर्वाधिक खर्च झाला असून, एकूण खर्चापैकी 40% खर्च मजुरीसाठी झाला आहे. त्यानंतर बियाण्यांवर 25%, खतांवर 20% आणि कीटकनाशकांवर 15% खर्च झाला आहे.\n\nयामुळे तुमच्या शेतीच्या खर्चामध्ये मजुरीचा सर्वात मोठा वाटा आहे, तर कीटकनाशकांवरील खर्च तुलनेने कमी आहे.';

  const handleSpeak = async () => {
    if (isPlaying) {
      voiceService.stopActiveAudio();
      setIsPlaying(false);
      return;
    }
    setIsPlaying(true);
    try {
      const audioBlob = await voiceService.synthesizeSpeech(explanationText, state.language);
      voiceService.playAudioBlob(audioBlob, {
        onEnded: () => setIsPlaying(false),
        onError: () => setIsPlaying(false),
      });
    } catch (err) {
      console.error('Explanation speech error:', err);
      setIsPlaying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex flex-col justify-end select-none animate-fade-in">
      {/* Click outside backdrop to close */}
      <div className="flex-1" onClick={() => store.setScreen('farm_topic')} />

      {/* Slide-up Sheet */}
      <div className="bg-white rounded-t-[2.5rem] p-6 max-w-md mx-auto w-full shadow-2xl flex flex-col gap-4 max-h-[90vh] overflow-y-auto border-t border-stone-200">
        {/* Header with Close Button */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => store.setScreen('farm_topic')}
            className="w-9 h-9 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-stone-700 active:scale-95 transition-transform"
          >
            <X size={18} />
          </button>

          <h3 className="text-base font-bold text-stone-900 tracking-tight text-center flex-1 pr-9">
            {t.total_farm_expenses}
          </h3>
        </div>

        {/* Donut Chart */}
        <div className="py-1">
          <DonutChart title="" />
        </div>

        {/* Explanation Section */}
        <div className="bg-stone-50 rounded-2xl p-4 border border-stone-100">
          <h4 className="text-xs font-bold text-stone-900 uppercase tracking-wider mb-2">
            {t.explanation}
          </h4>
          <p className="text-xs font-medium text-stone-700 leading-relaxed whitespace-pre-line">
            {explanationText}
          </p>
        </div>

        {/* Speak Out Button */}
        <button
          onClick={handleSpeak}
          className={`w-full py-3.5 px-6 rounded-full bg-stone-200/90 hover:bg-stone-300 text-stone-900 font-semibold text-xs flex items-center justify-center gap-2 active:scale-98 transition-all ${
            isPlaying ? 'ring-2 ring-stone-600 animate-pulse' : ''
          }`}
        >
          <Volume2 size={16} className={isPlaying ? 'text-amber-700' : ''} />
          <span>{isPlaying ? t.speaking : t.explain_this}</span>
        </button>
      </div>
    </div>
  );
};
