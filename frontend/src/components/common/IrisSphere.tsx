import React from 'react';
import figmaOrb from '../../assets/figma_orb.png';

interface IrisSphereProps {
  size?: number;
  isPulsing?: boolean;
  className?: string;
  onClick?: () => void;
}

export const IrisSphere: React.FC<IrisSphereProps> = ({
  size = 240,
  isPulsing = false,
  className = '',
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className={`relative flex items-center justify-center cursor-pointer select-none transition-transform duration-300 ${
        isPulsing ? 'scale-105' : 'hover:scale-102'
      } ${className}`}
      style={{ width: size, height: size }}
    >
      {/* Outer ambient warm glow matching Figma */}
      <div
        className={`absolute inset-0 rounded-full blur-2xl transition-all duration-700 ${
          isPulsing ? 'opacity-95 scale-115' : 'opacity-60'
        }`}
        style={{
          background: 'radial-gradient(circle, rgba(175, 90, 52, 0.65) 0%, rgba(110, 48, 25, 0.25) 60%, transparent 100%)',
        }}
      />

      {/* Authentic Figma Orb Asset */}
      <img
        src={figmaOrb}
        alt="DAV Voice Iris"
        className={`relative z-10 rounded-full object-cover drop-shadow-[0_10px_25px_rgba(50,20,10,0.4)] transition-all duration-500 ${
          isPulsing ? 'animate-pulse' : ''
        }`}
        style={{ width: size, height: size }}
      />
    </div>
  );
};
