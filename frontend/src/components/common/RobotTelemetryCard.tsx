import React, { useEffect, useState } from 'react';
import { Wifi, WifiOff, Battery, BatteryCharging, BatteryWarning, Navigation, Compass, Gauge, AlertTriangle, Radio } from 'lucide-react';
import { RobotStatusSummary } from '../../types';
import { robotTelemetryService } from '../../services/robotTelemetryService';

interface RobotTelemetryCardProps {
  onOpenDetails?: () => void;
}

export const RobotTelemetryCard: React.FC<RobotTelemetryCardProps> = ({ onOpenDetails }) => {
  const [status, setStatus] = useState<RobotStatusSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    // Initial fetch
    robotTelemetryService.getStatus()
      .then((data) => {
        if (isMounted) {
          setStatus(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.warn('Telemetry status fetch error:', err);
        if (isMounted) setLoading(false);
      });

    // Setup live WebSocket feed
    let ws: WebSocket | null = null;
    try {
      ws = robotTelemetryService.connectLiveFeed((msg) => {
        if (!isMounted) return;
        if ('type' in msg && msg.type === 'INIT_STATUS') {
          setStatus(msg.data);
        } else if ('temperature_c' in msg) {
          // Packet update
          setStatus((prev) => {
            if (!prev) return null;
            return {
              ...prev,
              current_temperature_c: msg.temperature_c ?? prev.current_temperature_c,
              current_humidity_pct: msg.humidity_pct ?? prev.current_humidity_pct,
              total_distance_m: msg.distance_m ?? prev.total_distance_m,
              gps_fix_acquired: msg.gps_fix,
              latitude: msg.latitude,
              longitude: msg.longitude,
              battery_voltage: msg.battery_voltage ?? prev.battery_voltage,
              connection_status: 'ONLINE',
              seconds_since_last_packet: 0,
              obstacle_distance_cm: msg.obstacle_distance_cm ?? prev.obstacle_distance_cm,
            };
          });
        }
      });
    } catch (e) {
      console.warn('WS connection skipped:', e);
    }

    // Polling backup every 15s to keep staleness updated
    const interval = setInterval(() => {
      robotTelemetryService.getStatus()
        .then((data) => {
          if (isMounted) setStatus(data);
        })
        .catch(console.warn);
    }, 15000);

    return () => {
      isMounted = false;
      clearInterval(interval);
      if (ws) ws.close();
    };
  }, []);

  if (loading) {
    return (
      <div className="w-full bg-white/80 rounded-2xl p-4 border border-stone-200/80 shadow-sm mb-4 animate-pulse">
        <div className="h-4 bg-stone-200 rounded w-1/3 mb-2"></div>
        <div className="h-6 bg-stone-200 rounded w-2/3"></div>
      </div>
    );
  }

  const isOnline = status?.connection_status === 'ONLINE';
  const isStale = status?.connection_status === 'STALE';
  const isDisconnected = !status || status.connection_status === 'DISCONNECTED';

  return (
    <div className="w-full bg-white rounded-3xl p-5 border border-stone-200/90 shadow-sm mb-5 transition-all">
      {/* Header: Status Pill & Battery */}
      <div className="flex items-center justify-between pb-3 border-b border-stone-100">
        <div className="flex items-center gap-2">
          <div className="relative flex items-center justify-center">
            {isOnline ? (
              <span className="flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
            ) : isStale ? (
              <span className="h-3 w-3 rounded-full bg-amber-500"></span>
            ) : (
              <span className="h-3 w-3 rounded-full bg-stone-400"></span>
            )}
          </div>
          <span className="text-xs font-bold uppercase tracking-wider text-stone-700">
            {status?.robot_id || 'DAV-ROBOT-01'}
          </span>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
            isOnline ? 'bg-emerald-100 text-emerald-800' : isStale ? 'bg-amber-100 text-amber-800' : 'bg-stone-200 text-stone-600'
          }`}>
            {status?.connection_status || 'OFFLINE'}
          </span>
        </div>

        {/* Battery State */}
        <div className="flex items-center gap-1.5 text-xs font-semibold text-stone-700">
          {status?.is_battery_low ? (
            <BatteryWarning size={16} className="text-rose-500" />
          ) : (
            <Battery size={16} className="text-emerald-600" />
          )}
          <span>{status?.battery_voltage ? `${status.battery_voltage.toFixed(1)}V` : '--'}</span>
          {status?.battery_percent !== undefined && (
            <span className="text-[11px] text-stone-500">({status.battery_percent}%)</span>
          )}
        </div>
      </div>

      {/* Main Grid: Onboard Temperature, Humidity, Distance, GPS Fix */}
      <div className="grid grid-cols-2 gap-3 pt-3.5 pb-2">
        {/* Onboard Temperature & Humidity from DHT22 */}
        <div className="bg-stone-50/90 rounded-2xl p-3 flex flex-col justify-between border border-stone-100">
          <span className="text-[11px] font-medium text-stone-500">DHT22 Microclimate</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-black text-stone-800">
              {status?.current_temperature_c !== null && status?.current_temperature_c !== undefined
                ? `${Math.round(status.current_temperature_c)}°C`
                : '--'}
            </span>
            <span className="text-xs text-stone-600 font-semibold">
              / {status?.current_humidity_pct !== null && status?.current_humidity_pct !== undefined
                ? `${Math.round(status.current_humidity_pct)}%`
                : '--'}
            </span>
          </div>
          <span className="text-[10px] text-stone-400 mt-1">Air Temp & Humidity</span>
        </div>

        {/* Wheel Encoder Distance (Equation 1) */}
        <div className="bg-stone-50/90 rounded-2xl p-3 flex flex-col justify-between border border-stone-100">
          <span className="text-[11px] font-medium text-stone-500">Distance Travelled</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-black text-stone-800">
              {status?.total_distance_m !== undefined ? status.total_distance_m.toFixed(1) : '0.0'}
            </span>
            <span className="text-xs font-bold text-stone-600">m</span>
          </div>
          <span className="text-[10px] text-stone-400 mt-1">Wheel Encoder Pulses</span>
        </div>
      </div>

      {/* GPS Fix and Location Row */}
      <div className="mt-1 p-2.5 rounded-2xl bg-stone-50/70 border border-stone-100 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <Navigation size={14} className={status?.gps_fix_acquired ? "text-emerald-600" : "text-stone-400"} />
          <span className="font-semibold text-stone-700">
            {status?.gps_fix_acquired
              ? `${status.latitude?.toFixed(4)}°N, ${status.longitude?.toFixed(4)}°E`
              : 'GPS: Searching Fix (Honest Status)'}
          </span>
        </div>

        {status?.obstacle_distance_cm !== null && status?.obstacle_distance_cm !== undefined && (
          <div className="flex items-center gap-1 font-semibold text-stone-600 text-[11px]">
            <Radio size={12} className="text-amber-600" />
            <span>Obs: {Math.round(status.obstacle_distance_cm)}cm</span>
          </div>
        )}
      </div>

      {/* Recency notice if stale */}
      {isStale && status?.seconds_since_last_packet && (
        <div className="mt-2 text-[10px] text-amber-700 bg-amber-50 px-2.5 py-1 rounded-xl flex items-center gap-1.5 border border-amber-200">
          <AlertTriangle size={12} />
          <span>Last packet received {Math.round(status.seconds_since_last_packet)}s ago (Stale)</span>
        </div>
      )}
    </div>
  );
};
