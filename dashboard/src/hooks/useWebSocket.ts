import { useEffect, useRef } from 'react';
import { useAppStore } from '../stores/appStore';
import type { WSMessage, HealthResponse } from '../types';

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>();
  const { setConnected, setServices, setModules, setUptime, addSignal, setRisk, updatePrice } = useAppStore();

  // Poll /health every 30 seconds as a fallback for infrastructure status
  useEffect(() => {
    async function fetchHealth() {
      try {
        const res = await fetch('/health');
        if (res.ok) {
          const data: HealthResponse = await res.json();
          setServices(data.services);
          setUptime(data.uptime_seconds);
        }
      } catch {
        // Backend not available yet
      }
    }

    fetchHealth();
    const interval = setInterval(fetchHealth, 30_000);
    return () => clearInterval(interval);
  }, [setServices, setUptime]);

  // WebSocket connection for real-time updates
  useEffect(() => {
    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/feed`);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
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
              const data = msg.data as {
                uptime?: number;
                services?: Record<string, { service: string; status: string }>;
                modules?: Record<string, any>;
              };
              if (data.uptime) setUptime(data.uptime);
              if (data.services) setServices(data.services);
              if (data.modules) setModules(data.modules);
              break;
            }
            case 'price': {
              const data = msg.data as {
                symbol?: string;
                price?: number;
                timestamp?: string;
                open?: number;
                high?: number;
                low?: number;
                close?: number;
                type?: string;
              };
              if (data.symbol) {
                updatePrice(data.symbol, {
                  price: data.price ?? data.close ?? 0,
                  timestamp: data.timestamp ?? new Date().toISOString(),
                  open: data.open,
                  high: data.high,
                  low: data.low,
                  close: data.close,
                  type: data.type,
                });
              }
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
  }, [setConnected, setServices, setModules, setUptime, addSignal, setRisk, updatePrice]);
}
