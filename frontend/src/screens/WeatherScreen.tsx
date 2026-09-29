import React, { useEffect, useState } from 'react';
import { CloudRain, Sun, Cloud, Droplets, Mic, Play, HelpCircle, Check, ArrowRight } from 'lucide-react';
import { TopBar } from '../components/common/TopBar';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { weatherService } from '../services/weatherService';
import { voiceService } from '../services/voiceService';
import { AgriculturalWeather } from '../types';

export const WeatherScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [weather, setWeather] = useState<AgriculturalWeather | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function fetchWeather() {
      setLoading(true);
      setError(null);
      try {
        const data = await weatherService.getCurrentWeather('Pune, MH', state.language);
        if (isMounted) setWeather(data);
      } catch (err: any) {
        console.error('Weather load error:', err);
        if (isMounted) setError(t.error_occurred);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    fetchWeather();
    return () => {
      isMounted = false;
    };
  }, [state.language]);

  const handlePlayAdvisory = async () => {
    if (!weather) return;
    setIsPlayingAudio(true);
    const advisoryText =
      state.language === 'en'
        ? weather.irrigation_advisory_en
        : state.language === 'hi'
        ? weather.irrigation_advisory_hi
        : weather.irrigation_advisory_mr;

    try {
      const audioBlob = await voiceService.synthesizeSpeech(advisoryText, state.language);
      const audio = voiceService.playAudioBlob(audioBlob);
      audio.onended = () => setIsPlayingAudio(false);
    } catch (err) {
      setIsPlayingAudio(false);
    }
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const rainfallMm = weather?.expected_rainfall_mm ?? 40;
  const advisory =
    state.language === 'en'
      ? weather?.irrigation_advisory_en || t.no_irrigation_needed
      : state.language === 'hi'
      ? weather?.irrigation_advisory_hi || t.no_irrigation_needed
      : weather?.irrigation_advisory_mr || t.no_irrigation_needed;

  return (
    <div className="w-full min-h-screen bg-[#e8e5df] flex flex-col justify-between pb-12 select-none">
      {/* Top Header */}
      <TopBar showBack={true} onBack={() => store.setScreen('home')} />

      {/* Main Content Area */}
      <div className="flex-1 px-6 flex flex-col justify-start gap-5 max-w-md mx-auto w-full pt-1">
        {error && (
          <div className="w-full bg-red-100 border border-red-300 text-red-800 text-xs px-4 py-2.5 rounded-2xl text-center">
            {error}
          </div>
        )}

        {/* Rainfall Highlight Card */}
        <div className="flex items-center justify-between pt-2">
          <div>
            <div className="flex items-baseline gap-1">
              <span className="text-5xl font-black text-stone-900 tracking-tighter">
                {rainfallMm}
              </span>
              <span className="text-xl font-bold text-stone-700">mm</span>
            </div>
            <p className="text-stone-800 font-semibold text-sm mt-0.5">
              {t.rain_expected_today}
            </p>
          </div>

          {/* Vertical Water Tank Indicator */}
          <div className="w-12 h-20 rounded-2xl bg-white border border-stone-300 p-1 flex flex-col justify-end shadow-sm">
            <div
              className="w-full rounded-xl bg-[#60a5fa] transition-all duration-700"
              style={{ height: `${Math.min(100, (rainfallMm / 50) * 100)}%` }}
            />
          </div>
        </div>

        {/* 4 Time Slots (Morning, Afternoon, Evening, Night) */}
        <div className="grid grid-cols-4 gap-2 pt-2">
          {[
            { label: t.morning, icon: Sun, active: false, time: '08:00' },
            { label: t.afternoon, icon: CloudRain, active: true, time: '14:00' },
            { label: t.evening, icon: CloudRain, active: false, time: '18:00' },
            { label: t.night, icon: Cloud, active: false, time: '22:00' },
          ].map((slot, idx) => {
            const Icon = slot.icon;
            return (
              <div
                key={idx}
                className={`py-3 px-1 rounded-2xl flex flex-col items-center gap-1.5 transition-all ${
                  slot.active
                    ? 'bg-white shadow-sm border border-stone-200'
                    : 'bg-stone-300/40'
                }`}
              >
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center ${
                    slot.active ? 'bg-blue-50 text-blue-600' : 'text-stone-600'
                  }`}
                >
                  <Icon size={20} />
                </div>
                <span className="text-[11px] font-semibold text-stone-800 text-center">
                  {slot.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Forecast Details Text */}
        <p className="text-stone-700 text-xs font-medium px-1">
          {t.rain_duration}
        </p>

        {/* Rain Intensity Meter */}
        <div className="bg-white/80 rounded-2xl p-4 border border-stone-200/80 shadow-sm flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-xs font-semibold text-stone-800 mb-1.5">
              {t.how_heavy}
            </span>
            <div className="flex items-center gap-2">
              {[1, 2, 3, 4].map((drop) => (
                <div
                  key={drop}
                  className={`w-7 h-7 rounded-full flex items-center justify-center ${
                    drop <= 3 ? 'bg-blue-500 text-white' : 'bg-stone-300 text-stone-500'
                  }`}
                >
                  <Droplets size={14} className="fill-current" />
                </div>
              ))}
            </div>
          </div>
          <span className="text-xs font-bold text-stone-900 pr-2">
            {t.heavy_rain}
          </span>
        </div>

        {/* Agricultural Advisory Banner */}
        <div className="w-full py-3.5 px-4 rounded-xl bg-white border border-stone-200 text-center text-xs font-semibold text-stone-900 shadow-sm">
          {advisory}
        </div>

        {/* Action Controls Bar */}
        <div className="flex items-center justify-center gap-4 py-2">
          {/* Mic */}
          <button
            onClick={() => store.setScreen('listening')}
            className="w-12 h-12 rounded-full bg-white border border-stone-300 flex items-center justify-center shadow-sm active:scale-95 transition-all text-stone-800 hover:bg-stone-50"
          >
            <Mic size={18} />
          </button>

          {/* Audio Playback of Advisory */}
          <button
            onClick={handlePlayAdvisory}
            className={`w-12 h-12 rounded-full bg-white border border-stone-300 flex items-center justify-center shadow-sm active:scale-95 transition-all text-stone-800 hover:bg-stone-50 ${
              isPlayingAudio ? 'ring-2 ring-blue-500 animate-pulse' : ''
            }`}
          >
            <Play size={18} className="fill-stone-800 ml-0.5" />
          </button>

          {/* Help */}
          <button
            onClick={() => {}}
            className="w-12 h-12 rounded-full bg-white border border-stone-300 flex items-center justify-center shadow-sm active:scale-95 transition-all text-stone-800 hover:bg-stone-50"
          >
            <HelpCircle size={18} />
          </button>
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          className="w-full py-3.5 rounded-full bg-white hover:bg-stone-50 text-stone-900 font-bold text-sm shadow-sm border border-stone-300 active:scale-98 transition-all flex items-center justify-center gap-2"
        >
          {saved ? (
            <>
              <Check size={16} className="text-green-600" />
              <span>{t.saved_success}</span>
            </>
          ) : (
            <span>{t.save_advisory}</span>
          )}
        </button>

        {/* Continue to Home Dashboard Button */}
        <button
          onClick={() => store.setScreen('home')}
          className="w-full py-3.5 rounded-full bg-stone-900 hover:bg-stone-800 text-white font-bold text-sm shadow-md active:scale-98 transition-all flex items-center justify-center gap-2 mt-1"
        >
          <span>{state.language === 'en' ? 'Continue to Home' : state.language === 'hi' ? 'होम डैशबोर्ड पर जाएं' : 'मुख्य पृष्ठावर जा'}</span>
          <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
};
