import React from 'react';
import farmerAvatarImg from '../../assets/farmer_avatar.png';

interface FarmerAvatarProps {
  size?: number;
  className?: string;
  onClick?: () => void;
}

export const FarmerAvatar: React.FC<FarmerAvatarProps> = ({
  size = 140,
  className = '',
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className={`relative rounded-full flex items-center justify-center overflow-hidden border-2 border-[#d6c4b2] shadow-sm bg-[#e8dacb] select-none ${className}`}
      style={{ width: size, height: size }}
    >
      <img
        src={farmerAvatarImg}
        alt="Farmer Avatar"
        className="w-full h-full object-cover object-center"
      />
    </div>
  );
};
