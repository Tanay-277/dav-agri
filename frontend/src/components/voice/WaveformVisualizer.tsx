import React, { useEffect, useState } from 'react';

interface WaveformVisualizerProps {
  isActive: boolean;
  audioLevel?: number; // 0.0 to 1.0
  className?: string;
}

export const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  isActive,
  audioLevel = 0,
  className = '',
}) => {
  const [points, setPoints] = useState<number[]>([10, 15, 25, 45, 60, 45, 30, 20, 10]);

  useEffect(() => {
    if (!isActive) {
      setPoints([5, 8, 12, 16, 20, 16, 12, 8, 5]);
      return;
    }

    const interval = setInterval(() => {
      const boost = Math.max(0.2, audioLevel * 1.8);
      setPoints((prev) =>
        prev.map(() => Math.floor((Math.random() * 50 + 15) * boost))
      );
    }, 100);

    return () => clearInterval(interval);
  }, [isActive, audioLevel]);

  const width = 300;
  const height = 60;
  const step = width / (points.length - 1);

  const pathD = points
    .map((p, idx) => {
      const x = idx * step;
      const y = height / 2 + (idx % 2 === 0 ? p / 2 : -p / 2);
      return `${idx === 0 ? 'M' : 'L'} ${x} ${y}`;
    })
    .join(' ');

  return (
    <div className={`w-full flex items-center justify-center overflow-hidden py-2 ${className}`}>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className="w-full max-w-xs">
        <path
          d={pathD}
          fill="none"
          stroke="rgba(255, 255, 255, 0.9)"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="transition-all duration-100"
        />
      </svg>
    </div>
  );
};
