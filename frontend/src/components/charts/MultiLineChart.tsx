import React from 'react';
import { StructuredVisualization } from '../../types';
import { useStore } from '../../state/store';
import { getTranslation } from '../../i18n';

interface MultiLineChartProps {
  data?: StructuredVisualization;
  title?: string;
  className?: string;
}

export const MultiLineChart: React.FC<MultiLineChartProps> = ({
  data,
  title,
  className = '',
}) => {
  const [state] = useStore();
  const t = getTranslation(state.language);
  const chartTitle = title !== undefined ? title : t.multi_crop_income_title;

  const defaultMonths =
    state.language === 'hi'
      ? ['मई', 'जून', 'जुलाई', 'अगस्त', 'सितंबर']
      : state.language === 'mr'
      ? ['मे', 'जून', 'जुलै', 'ऑगस्ट', 'सप्टेंबर']
      : ['May', 'June', 'July', 'Aug', 'Sept'];

  const months = data?.labels || defaultMonths;
  const datasets = data?.datasets || [
    { name: 'Crop A', color: '#f97316', data: [2200, 2400, 3100, 2600, 2800] },
    { name: 'Crop B', color: '#06b6d4', data: [1500, 1800, 2100, 1900, 2200] },
    { name: 'Crop C', color: '#a855f7', data: [1100, 1300, 1600, 1400, 1700] },
    { name: 'Crop D', color: '#3b82f6', data: [700, 950, 1200, 1100, 1350] },
  ];

  const maxY = 4000;
  const width = 320;
  const height = 180;
  const paddingX = 25;
  const paddingY = 25;
  const chartWidth = width - paddingX * 2 - 35;
  const chartHeight = height - paddingY * 2;

  // Build path strings for SVG
  const generatePath = (values: number[]) => {
    return values
      .map((val, idx) => {
        const x = paddingX + idx * (chartWidth / (values.length - 1));
        const y = paddingY + chartHeight - (val / maxY) * chartHeight;
        return `${idx === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
      })
      .join(' ');
  };

  return (
    <div className={`bg-white rounded-3xl p-5 shadow-sm border border-stone-200/80 ${className}`}>
      {chartTitle && <h3 className="text-stone-900 font-medium text-xs mb-3">{chartTitle}</h3>}

      <div className="relative flex justify-center">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto max-h-48 overflow-visible">
          {/* Y-axis grid & labels */}
          {[0, 1000, 2000, 3000, 4000].map((val) => {
            const y = paddingY + chartHeight - (val / maxY) * chartHeight;
            return (
              <g key={val}>
                <line
                  x1={paddingX}
                  y1={y}
                  x2={paddingX + chartWidth}
                  y2={y}
                  stroke="#f1f5f9"
                  strokeWidth="1"
                />
                <text
                  x={paddingX + chartWidth + 8}
                  y={y + 3}
                  textAnchor="start"
                  fontSize="8"
                  fill="#94a3b8"
                >
                  {val === 0 ? '0' : `${val / 1000}k`}
                </text>
              </g>
            );
          })}

          {/* Lines */}
          {datasets.map((ds, idx) => (
            <g key={idx}>
              <path
                d={generatePath(ds.data)}
                fill="none"
                stroke={ds.color}
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              {/* Highlight active point in center */}
              {idx === 0 && (
                <g>
                  <circle
                    cx={paddingX + 2 * (chartWidth / (ds.data.length - 1))}
                    cy={paddingY + chartHeight - (ds.data[2] / maxY) * chartHeight}
                    r="4.5"
                    fill="#ffffff"
                    stroke={ds.color}
                    strokeWidth="2.5"
                  />
                </g>
              )}
            </g>
          ))}

          {/* X-axis labels */}
          {months.map((m, idx) => {
            const x = paddingX + idx * (chartWidth / (months.length - 1));
            return (
              <text
                key={idx}
                x={x}
                y={height - 2}
                textAnchor="middle"
                fontSize="9"
                fill="#64748b"
              >
                {m}
              </text>
            );
          })}
        </svg>
      </div>
    </div>
  );
};
