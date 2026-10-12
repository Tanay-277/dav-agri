import { apiRequest } from './apiClient';
import { RobotStatusSummary, RobotTelemetryItem } from '../types';

export const robotTelemetryService = {
  /** Fetch current robot status summary including staleness and battery */
  async getStatus(robotId: string = 'dav_robot_01'): Promise<RobotStatusSummary> {
    return apiRequest<RobotStatusSummary>(`/telemetry/status?robot_id=${encodeURIComponent(robotId)}`);
  },

  /** Fetch timestamped telemetry history for graphs */
  async getHistory(robotId: string = 'dav_robot_01', limit: number = 50): Promise<RobotTelemetryItem[]> {
    return apiRequest<RobotTelemetryItem[]>(`/telemetry/history?robot_id=${encodeURIComponent(robotId)}&limit=${limit}`);
  },

  /** Send a telemetry packet (used by robot simulator or device test) */
  async sendPacket(packet: Partial<RobotTelemetryItem>): Promise<RobotTelemetryItem> {
    return apiRequest<RobotTelemetryItem>('/telemetry/packet', {
      method: 'POST',
      body: JSON.stringify(packet),
    });
  },

  /** Connect to WebSocket live feed for real-time updates without polling */
  connectLiveFeed(
    onData: (data: RobotTelemetryItem | { type: string; data: RobotStatusSummary }) => void,
    onError?: (err: Event) => void
  ): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Vite proxy handles /api/v1 -> localhost:8000
    const wsUrl = `${protocol}//${window.location.host}/api/v1/telemetry/live`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        onData(parsed);
      } catch (e) {
        console.warn('WS JSON parse error:', e);
      }
    };

    if (onError) {
      ws.onerror = onError;
    }

    return ws;
  },
};
