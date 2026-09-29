import React from 'react';
import { StructuredVisualization } from '../../types';
import { useStore } from '../../state/store';
import { getTranslation } from '../../i18n';

interface StackedBarChartProps {
  data?: StructuredVisualization;
  title?: string;
  className?: string;
}

export const StackedBarChart: React.FC<StackedBarChartProps> = ({
  data,
  title,
  className = '',
}) => {
  const [state] = useStore();
  const t = getTranslation(state.language);
  const chartTitle = title !== undefined ? title : (data?.title || t.cotton_income_title);
  const labels = data?.labels || ['2021', '2022', '2023', '2024', '2025'];
  // Default values matching Figma Screen 12
  const datasets = data?.datasets || [
    { name: 'Base', color: '#8b5cf6', data: [20, 25, 45, 60, 65] },
    { name: 'Secondary', color: '#14b8a6', data: [40, 55, 65, 80, 95] },
    { name: 'Bonus', color: '#f97316', data: [30, 45, 40, 40, 40] },
  ];

  const maxY = 200;
  const height = 180;
  const width = 320;
  const paddingX = 40;
  const paddingY = 25;
  const chartHeight = height - paddingY * 1.5;
  const chartWidth = width - paddingX * 1.5;

  return (
    <div className={`bg-white rounded-3xl p-5 shadow-sm border border-stone-200/80 ${className}`}>
      {chartTitle && <h3 className="text-stone-900 font-semibold text-sm mb-3">{chartTitle}</h3>}

      <div className="relative flex justify-center">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto max-h-48 overflow-visible">
          {/* Grid lines & Y-axis labels */}
          {[0, 50, 100, 150, 200].map((val) => {
            const y = chartHeight - (val / maxY) * chartHeight + paddingY;
            return (
              <g key={val}>
                <line
                  x1={paddingX}
                  y1={y}
                  x2={width - 20}
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                />
                <text
                  x={width - 15}
                  y={y + 3}
                  textAnchor="start"
                  fontSize="9"
                  fill="#9ca3af"
                >
                  {val}
                </text>
              </g>
            );
          })}

          {/* Stacked Bars */}
          {labels.map((label, colIdx) => {
            const barWidth = 18;
            const x = paddingX + (colIdx * (chartWidth / (labels.length - 1 || 1))) - (barWidth / 2);
            let currentBaseY = chartHeight + paddingY;

            return (
              <g key={colIdx}>
                {datasets.map((ds, dsIdx) => {
                  const val = ds.data[colIdx] || 0;
                  const barH = (val / maxY) * chartHeight;
                  const barY = currentBaseY - barH;
                  currentBaseY = barY;

                  const isTop = dsIdx === datasets.length - 1;
                  const isBottom = dsIdx === 0;

                  return (
                    <rect
                      key={dsIdx}
                      x={x}
                      y={barY}
                      width={barWidth}
                      height={Math.max(0, barH)}
                      fill={ds.color}
                      rx={isTop ? 3 : 0}
                      ry={isTop ? 3 : 0}
                      className="transition-all duration-300"
                    />
                  );
                })}

                {/* X-axis label */}
                <text
                  x={x + barWidth / 2}
                  y={height - 2}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#4b5563"
                  fontWeight="500"
                >
                  {label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
};
