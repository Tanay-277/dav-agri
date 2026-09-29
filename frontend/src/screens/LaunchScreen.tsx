import React, { useEffect } from 'react';
import { IrisSphere } from '../components/common/IrisSphere';
import { useStore } from '../state/store';

export const LaunchScreen: React.FC = () => {
  const [, store] = useStore();

  useEffect(() => {
    store.loadInitialData();
  }, []);

  const handleLaunch = () => {
    store.proceedFromLaunch();
  };

  return (
    <div
      onClick={handleLaunch}
      className="w-full h-full min-h-[100dvh] bg-[#e8e5df] flex flex-col items-center justify-center p-6 select-none cursor-pointer"
    >
      <div className="flex flex-col items-center justify-center animate-fade-in">
        <IrisSphere size={240} isPulsing={true} onClick={handleLaunch} />
      </div>
    </div>
  );
};
