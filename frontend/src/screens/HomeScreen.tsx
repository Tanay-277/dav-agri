import React, { useEffect, useState } from 'react';
import { CloudRain, ShieldAlert, Sprout, Landmark, Mic, Sun } from 'lucide-react';
import { TopBar } from '../components/common/TopBar';
import { BottomNav } from '../components/common/BottomNav';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { weatherService } from '../services/weatherService';
import { queryService } from '../services/queryService';
import { AgriculturalWeather } from '../types';

export const HomeScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [weather, setWeather] = useState<AgriculturalWeather | null>(null);

  useEffect(() => {
    let isMounted = true;
    weatherService
      .getCurrentWeather('Pune, MH', state.language)
      .then((data) => {
        if (isMounted) setWeather(data);
      })
      .catch(console.warn);
    return () => {
      isMounted = false;
    };
  }, [state.language]);

  const handleCategoryClick = async (categoryIntent: string) => {
    let queryText = '';
    if (categoryIntent === 'weather') {
      store.setScreen('weather');
      return;
    } else if (categoryIntent === 'crop_protection') {
      queryText =
        state.language === 'en'
          ? 'Crop disease and preventive protection advisory'
          : state.language === 'hi'
          ? 'फसल सुरक्षा और रोग नियंत्रण सलाह'
          : 'पिकांचे संरक्षण आणि रोग नियंत्रण माहिती सांगा';
    } else if (categoryIntent === 'crop_prices') {
      queryText =
        state.language === 'en'
          ? 'Current market prices for cotton and wheat'
          : state.language === 'hi'
          ? 'कपास और गेहूं के ताजा मंडी भाव'
          : 'कापूस आणि गव्हाचे आजचे बाजारभाव सांगा';
    } else if (categoryIntent === 'gov_schemes') {
      queryText =
        state.language === 'en'
          ? 'Government schemes and subsidies for farmers'
          : state.language === 'hi'
          ? 'किसानों के लिए सरकारी योजनाएं और सब्सिडी'
          : 'शेतकऱ्यांसाठी सरकारी योजना आणि अनुदाने';
    }

    try {
      const res = await queryService.executeQuery(queryText, state.language);
      store.setProcessedResult(res);
      store.setScreen('processed');
    } catch (err) {
      store.setScreen('listening');
    }
  };

  const temp = weather ? Math.round(weather.temperature_c) : 27;

  return (
    <div className="w-full min-h-screen bg-[#e8e5df] flex flex-col justify-between pb-28 select-none">
      {/* Top Bar */}
      <TopBar />

      <div className="flex-1 px-6 max-w-md mx-auto w-full flex flex-col justify-between pt-2">
        {/* Weather Mini-Card Banner */}
        <div
          onClick={() => store.setScreen('weather')}
          className="w-full bg-white/70 hover:bg-white/90 rounded-2xl py-3 px-5 flex items-center justify-between border border-stone-200/80 shadow-sm cursor-pointer transition-all active:scale-98 mb-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-amber-100/80 flex items-center justify-center">
              <Sun size={20} className="text-amber-600" />
            </div>
            <span className="text-sm font-semibold text-stone-800">
              {t.summer_weather}
            </span>
          </div>

          <span className="text-sm font-bold text-stone-900">
            {temp}°C {t.city_pune}
          </span>
        </div>

        {/* 4 Category Grid Cards (2x2) */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {/* Card 1: Weather */}
          <button
            onClick={() => handleCategoryClick('weather')}
            className="h-32 bg-white rounded-3xl p-4 flex flex-col items-center justify-center gap-3 shadow-sm border border-stone-200/70 hover:shadow-md active:scale-96 transition-all"
          >
            <div className="w-12 h-12 rounded-2xl bg-stone-100 flex items-center justify-center text-stone-800">
              <CloudRain size={26} />
            </div>
            <span className="text-sm font-semibold text-stone-900 text-center">
              {t.weather_title}
            </span>
          </button>

          {/* Card 2: Crop Protection */}
          <button
            onClick={() => handleCategoryClick('crop_protection')}
            className="h-32 bg-white rounded-3xl p-4 flex flex-col items-center justify-center gap-3 shadow-sm border border-stone-200/70 hover:shadow-md active:scale-96 transition-all"
          >
            <div className="w-12 h-12 rounded-2xl bg-stone-100 flex items-center justify-center text-stone-800">
              <ShieldAlert size={26} />
            </div>
            <span className="text-sm font-semibold text-stone-900 text-center">
              {t.crop_protection}
            </span>
          </button>

          {/* Card 3: Crop Prices */}
          <button
            onClick={() => handleCategoryClick('crop_prices')}
            className="h-32 bg-white rounded-3xl p-4 flex flex-col items-center justify-center gap-3 shadow-sm border border-stone-200/70 hover:shadow-md active:scale-96 transition-all"
          >
            <div className="w-12 h-12 rounded-2xl bg-stone-100 flex items-center justify-center text-stone-800">
              <Sprout size={26} />
            </div>
            <span className="text-sm font-semibold text-stone-900 text-center">
              {t.crop_prices}
            </span>
          </button>

          {/* Card 4: Government Schemes */}
          <button
            onClick={() => handleCategoryClick('gov_schemes')}
            className="h-32 bg-white rounded-3xl p-4 flex flex-col items-center justify-center gap-3 shadow-sm border border-stone-200/70 hover:shadow-md active:scale-96 transition-all"
          >
            <div className="w-12 h-12 rounded-2xl bg-stone-100 flex items-center justify-center text-stone-800">
              <Landmark size={26} />
            </div>
            <span className="text-sm font-semibold text-stone-900 text-center">
              {t.gov_schemes}
            </span>
          </button>
        </div>

        {/* Big Central Mic Button */}
        <div className="flex flex-col items-center justify-center my-auto pb-4">
          <button
            onClick={() => store.setScreen('listening')}
            className="w-20 h-20 rounded-full bg-white border-2 border-stone-300 shadow-float flex items-center justify-center active:scale-92 transition-transform duration-200 hover:shadow-xl group"
          >
            <Mic size={32} className="text-stone-800 group-hover:scale-110 transition-transform" />
          </button>
          <span className="text-xs font-semibold text-stone-700 mt-3 text-center">
            {t.tap_to_speak}
          </span>
        </div>
      </div>

      {/* Persistent Bottom Nav */}
      <BottomNav activeScreen="home" />
    </div>
  );
};
