import { useEffect, useRef } from 'react';
import { useAppStore } from '../stores/appStore';
import type { WSMessage } from '../types';

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>();
  const { setConnected, setServices, setUptime, addSignal, setRisk } = useAppStore();

  useEffect(() => {
    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/feed`);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        // Start ping interval
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
        ws.addEventListener('close', () => clearInterval(pingInterval));
      };

      ws.onmessage = (event) => {
        try {
          const msg: WSMessage = JSON.parse(event.data);
          switch (msg.type) {
            case 'status': {
              const data = msg.data as { uptime?: number; services?: Record<string, unknown> };
              if (data.uptime) setUptime(data.uptime);
              if (data.services) setServices(data.services as Record<string, { service: string; status: string }>);
              break;
            }
            case 'signal':
              addSignal(msg.data as Parameters<typeof addSignal>[0]);
              break;
            case 'risk':
              setRisk(msg.data as Parameters<typeof setRisk>[0]);
              break;
          }
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        setConnected(false);
        // Reconnect after delay
        reconnectTimer.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    return () => {
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [setConnected, setServices, setUptime, addSignal, setRisk]);
}
