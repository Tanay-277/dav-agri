import React, { useEffect, useState } from 'react';
import { Sprout, Plus, Volume2 } from 'lucide-react';
import { TopBar } from '../components/common/TopBar';
import { BottomNav } from '../components/common/BottomNav';
import { MultiLineChart } from '../components/charts/MultiLineChart';
import { DonutChart } from '../components/charts/DonutChart';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { farmService } from '../services/farmService';
import { voiceService } from '../services/voiceService';
import { Crop, ExpenseBreakdown } from '../types';

export const FarmTopicScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [selectedCrop, setSelectedCrop] = useState('crop_cotton');
  const [expenses, setExpenses] = useState<ExpenseBreakdown | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newYear, setNewYear] = useState('2026');
  const [newQty, setNewQty] = useState('25');
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    farmService.listCrops().then(setCrops).catch(console.warn);
    farmService.getExpenseBreakdown(state.language).then(setExpenses).catch(console.warn);
  }, [state.language]);

  const handleOpenExplanation = () => {
    store.setScreen('topic_explanation');
  };

  const handleAddRecord = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQty) return;
    setAdding(true);
    try {
      await farmService.addProduction({
        crop_id: selectedCrop,
        year: parseInt(newYear) || 2026,
        quantity_quintals: parseFloat(newQty) || 20.0,
        revenue_inr: (parseFloat(newQty) || 20.0) * 8000,
      });
      setShowAddModal(false);
      // Refresh data
      farmService.getExpenseBreakdown(state.language).then(setExpenses).catch(console.warn);
    } catch (err) {
      console.warn('Failed to add record:', err);
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="w-full min-h-screen bg-[#e8e5df] flex flex-col justify-between pb-28 select-none relative">
      {/* Top Bar */}
      <TopBar showBack={true} backText={t.back} onBack={() => store.setScreen('farm')} />

      <div className="flex-1 px-6 max-w-md mx-auto w-full flex flex-col gap-5 overflow-y-auto pt-1">
        {/* Header: उत्पादन icon & + नवीन नोंद Button */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center text-stone-800 shadow-sm border border-stone-200">
              <Sprout size={18} />
            </div>
            <span className="text-base font-bold text-stone-900 tracking-tight">
              {t.production}
            </span>
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="py-2 px-4 rounded-full bg-white hover:bg-stone-50 border border-stone-200 shadow-sm text-xs font-semibold text-stone-900 flex items-center gap-1.5 active:scale-95 transition-all"
          >
            <Plus size={14} />
            <span>{t.new_record}</span>
          </button>
        </div>

        {/* Crop Filter Pills */}
        <div className="flex items-center gap-2.5 overflow-x-auto pb-1">
          {crops.map((c) => {
            const isSelected = selectedCrop === c.id;
            const label =
              state.language === 'en' ? c.name_en : state.language === 'hi' ? c.name_hi : c.name_mr;
            return (
              <button
                key={c.id}
                onClick={() => setSelectedCrop(c.id)}
                className={`py-2 px-5 rounded-full text-xs font-semibold shadow-sm transition-all active:scale-95 whitespace-nowrap ${
                  isSelected
                    ? 'bg-white text-stone-900 border border-stone-300'
                    : 'bg-stone-300/60 text-stone-700 hover:bg-stone-300'
                }`}
              >
                {label}
              </button>
            );
          })}
        </div>

        {/* Chart 1: कापूस पिकांमधून मिळालेले उत्पन्न */}
        <div className="flex flex-col gap-2">
          <MultiLineChart title={t.cotton_income_title} />

          {/* Button: मला हे समजावून सांगा */}
          <button
            onClick={handleOpenExplanation}
            className="w-full py-3 rounded-2xl bg-white/90 hover:bg-white border border-stone-200 shadow-sm text-xs font-semibold text-stone-900 flex items-center justify-center gap-2 active:scale-98 transition-all"
          >
            <Volume2 size={15} />
            <span>{t.explain_this}</span>
          </button>
        </div>

        {/* Chart 2: माझ्या शेतीचा एकूण खर्च (Donut Chart) */}
        <div className="flex flex-col gap-2">
          <div onClick={handleOpenExplanation} className="cursor-pointer">
            <DonutChart data={expenses || undefined} title={t.total_farm_expenses} />
          </div>

          {/* Button: मला हे समजावून सांगा */}
          <button
            onClick={handleOpenExplanation}
            className="w-full py-3 rounded-2xl bg-white/90 hover:bg-white border border-stone-200 shadow-sm text-xs font-semibold text-stone-900 flex items-center justify-center gap-2 active:scale-98 transition-all"
          >
            <Volume2 size={15} />
            <span>{t.explain_this}</span>
          </button>
        </div>
      </div>

      {/* New Record Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-6">
          <div className="bg-white rounded-3xl p-6 w-full max-w-xs shadow-float border border-stone-200 flex flex-col gap-4">
            <h3 className="text-base font-bold text-stone-900">{t.new_record}</h3>

            <form onSubmit={handleAddRecord} className="flex flex-col gap-3">
              <div>
                <label className="text-xs font-semibold text-stone-700 block mb-1">{t.year}</label>
                <input
                  type="number"
                  value={newYear}
                  onChange={(e) => setNewYear(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-stone-300 text-xs font-medium"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-stone-700 block mb-1">
                  {t.quantity_quintals}
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={newQty}
                  onChange={(e) => setNewQty(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-stone-300 text-xs font-medium"
                />
              </div>

              <div className="flex items-center gap-2 mt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2.5 rounded-xl border border-stone-300 text-xs font-medium text-stone-700"
                >
                  {t.cancel}
                </button>
                <button
                  type="submit"
                  disabled={adding}
                  className="flex-1 py-2.5 rounded-xl bg-stone-900 text-white text-xs font-semibold"
                >
                  {adding ? t.saving : t.save_changes}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Persistent Bottom Nav */}
      <BottomNav activeScreen="farm_topic" />
    </div>
  );
};
