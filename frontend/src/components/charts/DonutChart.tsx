import React from 'react';
import { ExpenseBreakdown } from '../../types';
import { useStore } from '../../state/store';
import { getTranslation } from '../../i18n';

interface DonutChartProps {
  data?: ExpenseBreakdown;
  title?: string;
  className?: string;
}

export const DonutChart: React.FC<DonutChartProps> = ({
  data,
  title,
  className = '',
}) => {
  const [state] = useStore();
  const t = getTranslation(state.language);
  const chartTitle = title !== undefined ? title : t.total_farm_expenses;

  const items = data?.breakdown || [
    { category: 'labor', label_en: 'Labor', label_hi: 'मजदूरी', label_mr: 'मजुरी', percentage: 40, color: '#8b5cf6' },
    { category: 'seeds', label_en: 'Seeds', label_hi: 'बीज', label_mr: 'बियाणे', percentage: 25, color: '#eab308' },
    { category: 'fertilizer', label_en: 'Fertilizer', label_hi: 'खाद', label_mr: 'खत', percentage: 20, color: '#f97316' },
    { category: 'pesticides', label_en: 'Pesticides', label_hi: 'कीटनाशक', label_mr: 'कीटकनाशके', percentage: 15, color: '#14b8a6' },
  ];

  const getLabel = (item: any) => {
    if (state.language === 'en') return item.label_en || item.label || item.label_mr;
    if (state.language === 'hi') return item.label_hi || item.label || item.label_mr;
    return item.label_mr || item.label || item.label_hi || item.label_en;
  };

  const size = 180;
  const strokeWidth = 52;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  let cumulativePercent = 0;

  return (
    <div className={`bg-white rounded-3xl p-5 shadow-sm border border-stone-200/80 ${className}`}>
      {chartTitle && <h3 className="text-stone-900 font-semibold text-sm mb-4 text-center">{chartTitle}</h3>}

      {/* SVG Donut / Pie */}
      <div className="flex justify-center items-center my-2">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="transform -rotate-90">
          {items.map((item, idx) => {
            const strokeDasharray = `${(item.percentage / 100) * circumference} ${circumference}`;
            const strokeDashoffset = -((cumulativePercent / 100) * circumference);
            cumulativePercent += item.percentage;

            return (
              <circle
                key={idx}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                fill="transparent"
                stroke={item.color}
                strokeWidth={strokeWidth}
                strokeDasharray={strokeDasharray}
                strokeDashoffset={strokeDashoffset}
                className="transition-all duration-500"
              />
            );
          })}
        </svg>
      </div>

      {/* Legend Grid */}
      <div className="grid grid-cols-2 gap-y-2 gap-x-4 mt-5 pt-3 border-t border-stone-100 text-xs text-stone-700">
        {items.map((item, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <span
              className="w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: item.color }}
            />
            <span className="truncate">
              {getLabel(item)}: <strong className="font-semibold text-stone-900">{item.percentage}%</strong>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
