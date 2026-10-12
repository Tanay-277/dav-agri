import React, { useState, useEffect } from 'react';
import {
  MapPin,
  Sprout,
  Grid,
  ChevronDown,
  Edit2,
  Check,
  X,
} from 'lucide-react';
import { TopBar } from '../components/common/TopBar';
import { BottomNav } from '../components/common/BottomNav';
import { FarmerAvatar } from '../components/common/FarmerAvatar';
import { useStore } from '../state/store';
import { getTranslation } from '../i18n';
import { profileService } from '../services/profileService';

export const EditProfileScreen: React.FC = () => {
  const [state, store] = useStore();
  const t = getTranslation(state.language);

  const [name, setName] = useState('Raj Patil');
  const [location, setLocation] = useState('Pune, MH');
  const [age, setAge] = useState(42);
  const [landLocation, setLandLocation] = useState('Plot No. 124/2, Kothrud');
  const [primaryCrop, setPrimaryCrop] = useState('Cotton');
  const [landSize, setLandSize] = useState('20 acres');
  const [irrigationType, setIrrigationType] = useState('Rain Fed');
  const [livestock, setLivestock] = useState('Cow, Goat, Buffalo');
  const [cropsGrown, setCropsGrown] = useState<string[]>(['Cotton', 'Wheat', 'Ragi']);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    if (state.profile) {
      setName(state.profile.name);
      setLocation(state.profile.location);
      setAge(state.profile.age);
      setLandLocation(state.profile.land_location || 'Plot No. 124/2, Kothrud');
      setPrimaryCrop(state.profile.primary_crop || 'Cotton');
      setLandSize(state.profile.land_size || '20 acres');
      setIrrigationType(state.profile.irrigation_type || 'Rain Fed');
      setLivestock(state.profile.livestock || 'Cow, Goat, Buffalo');
      setCropsGrown(state.profile.crops_grown || ['Cotton', 'Wheat', 'Ragi']);
    }
  }, [state.profile]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await profileService.updateProfile({
        name,
        location,
        age: Number(age),
        land_location: landLocation,
        primary_crop: primaryCrop,
        land_size: landSize,
        irrigation_type: irrigationType,
        livestock,
        crops_grown: cropsGrown,
      });
      store.setProfile(updated);
      setSavedSuccess(true);
      setTimeout(() => {
        setSavedSuccess(false);
        store.setScreen('profile');
      }, 1000);
    } catch (err) {
      // A silent failure here would look like the save worked. Say it did not.
      setNotice(t.save_failed);
      setTimeout(() => setNotice(null), 3000);
    } finally {
      setSaving(false);
    }
  };

  const [newCrop, setNewCrop] = useState('');

  // Adding a crop used to call window.prompt(), which is blocked or ignored in
  // some mobile browsers and in an installed PWA. It is a real inline field now.
  const handleAddCrop = () => {
    const cropName = newCrop.trim();
    if (cropName && !cropsGrown.includes(cropName)) {
      setCropsGrown([...cropsGrown, cropName]);
    }
    setNewCrop('');
  };

  const handleRemoveCrop = (crop: string) => {
    setCropsGrown(cropsGrown.filter((c) => c !== crop));
  };

  return (
    <div className="w-full min-h-screen bg-[#e8e5df] flex flex-col justify-between pb-28 select-none">
      {/* Top Bar with Back Arrow */}
      <TopBar showBack={true} onBack={() => store.setScreen('profile')} showLanguagePill={false} />

      <form onSubmit={handleSave} className="flex-1 px-6 max-w-md mx-auto w-full flex flex-col gap-4 overflow-y-auto pt-1">
        {/* Avatar with Edit Image button */}
        <div className="flex flex-col items-center gap-1.5 pt-1">
          <FarmerAvatar size={100} />
{/* Edit Image has no upload backend yet, so it reports that instead of
              accepting a tap and doing nothing. */}
            <button
              type="button"
              onClick={() => {
                setNotice(t.not_available_yet);
                setTimeout(() => setNotice(null), 2500);
              }}
              className="flex items-center gap-1.5 text-stone-800 text-xs font-semibold hover:text-stone-900 mt-1"
            >
            <Edit2 size={13} />
            <span>{t.edit_image}</span>
          </button>
        </div>

        {/* Name Input */}
        <div className="flex flex-col gap-1">
          <label className="text-xs font-semibold text-stone-800">{t.name}</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full py-3 px-4 rounded-2xl bg-white border border-stone-200 text-stone-900 text-xs font-semibold shadow-sm focus:outline-none focus:ring-2 focus:ring-stone-400"
          />
        </div>

        {/* Location & Age Row */}
        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-stone-800">{t.location}</label>
            <div className="relative flex items-center">
              <MapPin size={15} className="absolute left-3.5 text-stone-500" />
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full py-3 pl-9 pr-3 rounded-2xl bg-white border border-stone-200 text-stone-900 text-xs font-semibold shadow-sm focus:outline-none focus:ring-2 focus:ring-stone-400"
              />
            </div>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-stone-800">{t.age}</label>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(parseInt(e.target.value) || 0)}
              className="w-full py-3 px-4 rounded-2xl bg-white border border-stone-200 text-stone-900 text-xs font-semibold shadow-sm focus:outline-none focus:ring-2 focus:ring-stone-400"
            />
          </div>
        </div>

        {/* Section: Farm Details */}
        <div className="pt-2">
          <h3 className="text-xs font-bold text-stone-900 mb-2">{t.farm_details}</h3>

          {/* Land location */}
          <div className="flex flex-col gap-1 mb-3">
            <label className="text-[11px] font-semibold text-stone-700">{t.land_location}</label>
            <div className="relative flex items-center">
              <MapPin size={15} className="absolute left-3.5 text-stone-500" />
              <input
                type="text"
                value={landLocation}
                onChange={(e) => setLandLocation(e.target.value)}
                className="w-full py-3 pl-9 pr-3 rounded-2xl bg-white border border-stone-200 text-stone-900 text-xs font-semibold shadow-sm focus:outline-none"
              />
            </div>
          </div>

          {/* Crop & Land Size Row */}
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-stone-700">{t.primary_crop}</label>
              <div className="relative flex items-center">
                <Sprout size={15} className="absolute left-3.5 text-stone-500" />
                <input
                  type="text"
                  value={primaryCrop}
                  onChange={(e) => setPrimaryCrop(e.target.value)}
                  className="w-full py-3 pl-9 pr-3 rounded-2xl bg-white border border-stone-200 text-stone-900 text-xs font-semibold shadow-sm"
                />
              </div>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-stone-700">{t.land_size}</label>
              <div className="relative flex items-center">
                <Grid size={15} className="absolute left-3.5 text-stone-500" />
                <input
                  type="text"
                  value={landSize}
                  onChange={(e) => setLandSize(e.target.value)}
                  className="w-full py-3 pl-9 pr-3 rounded-2xl bg-white border border-stone-200 text-stone-900 text-xs font-semibold shadow-sm"
                />
              </div>
            </div>
          </div>

          {/* Irrigation & Livestock Row */}
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-stone-700">{t.irrigation_type}</label>
              <div className="relative">
                <select
                  value={irrigationType}
                  onChange={(e) => setIrrigationType(e.target.value)}
                  className="w-full py-3 px-4 rounded-2xl bg-white border border-stone-200 text-stone-900 text-xs font-semibold shadow-sm appearance-none focus:outline-none"
                >
                  <option value="Rain Fed">{t.irrigation_rainfed}</option>
                  <option value="Borewell">{t.irrigation_borewell}</option>
                  <option value="Canal">{t.irrigation_canal}</option>
                  <option value="Drip">{t.irrigation_drip}</option>
                </select>
                <ChevronDown size={15} className="absolute right-3.5 top-3.5 text-stone-500 pointer-events-none" />
              </div>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-stone-700">{t.livestock}</label>
              <input
                type="text"
                value={livestock}
                onChange={(e) => setLivestock(e.target.value)}
                className="w-full py-3 px-4 rounded-2xl bg-white border border-stone-200 text-stone-900 text-xs font-semibold shadow-sm"
              />
            </div>
          </div>

          {/* Crops Grown Tags */}
          <div className="flex flex-col gap-1.5 mb-2">
            <label className="text-[11px] font-semibold text-stone-700">{t.crops_grown}</label>
            <div className="flex items-center gap-2 flex-wrap">
              {/* Each crop is removable: "+" alone could only ever add, so a mistaken
                  entry was impossible to correct without editing the whole profile. */}
              {cropsGrown.map((crop, idx) => (
                <button
                  key={`${crop}-${idx}`}
                  type="button"
                  onClick={() => handleRemoveCrop(crop)}
                  aria-label={`${t.remove} ${crop}`}
                  className="py-1.5 pl-4 pr-3 rounded-full bg-white border border-stone-300 text-stone-900 text-xs font-semibold shadow-sm flex items-center gap-1.5 active:scale-95 transition-transform"
                >
                  <span>{crop}</span>
                  <X size={12} className="text-stone-500" />
                </button>
              ))}

              <input
                type="text"
                value={newCrop}
                onChange={(e) => setNewCrop(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddCrop();
                  }
                }}
                placeholder={t.add_crop}
                aria-label={t.add_crop}
                className="py-1.5 px-3 rounded-full bg-white border border-stone-300 text-stone-900 text-xs font-semibold w-32 focus:outline-none focus:ring-2 focus:ring-stone-400"
              />

              {newCrop.trim() && (
                <button
                  type="button"
                  onClick={handleAddCrop}
                  className="py-1.5 px-3 rounded-full bg-stone-800 text-white text-xs font-bold active:scale-95 transition-transform"
                >
                  {t.add}
                </button>
              )}
            </div>
          </div>
        </div>

        {notice && (
          <div className="text-center text-xs text-stone-700 bg-stone-200/80 py-2 px-3 rounded-xl">
            {notice}
          </div>
        )}

        {/* Save Changes Button */}
        <button
          type="submit"
          disabled={saving}
          className="w-full py-3.5 px-6 rounded-full bg-stone-900 hover:bg-stone-800 text-white font-bold text-xs shadow-md active:scale-98 transition-all flex items-center justify-center gap-2 mt-2"
        >
          {savedSuccess ? (
            <>
              <Check size={16} className="text-green-400" />
              <span>{t.saved_success}</span>
            </>
          ) : (
            <span>{saving ? t.saving : t.save_changes}</span>
          )}
        </button>
      </form>

      {/* Persistent Bottom Nav */}
      <BottomNav activeScreen="edit_profile" />
    </div>
  );
};
