import { useEffect, useState } from 'react';
import { Activity, Wifi, WifiOff } from 'lucide-react';
import { useAppStore } from '../stores/appStore';

export function Header() {
  const { connected, services } = useAppStore();
  const [clock, setClock] = useState('');

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setClock(
        now.toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
      );
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const serviceNames = ['postgres', 'redis', 'nats', 'questdb'];

  return (
    <header className="h-12 bg-apex-panel border-b border-apex-border flex items-center justify-between px-4 shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="text-apex-green font-bold text-lg tracking-widest glow-green">
            &#9651; APEX
          </span>
          <span className="text-apex-muted text-xs">v0.1.0</span>
        </div>
      </div>

      {/* Service status dots */}
      <div className="flex items-center gap-4">
        {serviceNames.map((name) => {
          const svc = services[name];
          const healthy = svc?.status === 'healthy';
          return (
            <div key={name} className="flex items-center gap-1.5">
              <div
                className={`w-2 h-2 rounded-full ${
                  healthy ? 'bg-apex-green pulse-dot' : 'bg-apex-red'
                }`}
              />
              <span className="text-[10px] text-apex-muted uppercase">{name}</span>
            </div>
          );
        })}
        <div className="w-px h-5 bg-apex-border mx-1" />
        <div className="flex items-center gap-1.5">
          {connected ? (
            <Wifi className="w-3.5 h-3.5 text-apex-green" />
          ) : (
            <WifiOff className="w-3.5 h-3.5 text-apex-red" />
          )}
          <span className={`text-[10px] ${connected ? 'text-apex-green' : 'text-apex-red'}`}>
            {connected ? 'LIVE' : 'OFFLINE'}
          </span>
        </div>
      </div>

      {/* Clock */}
      <div className="flex items-center gap-2">
        <Activity className="w-3.5 h-3.5 text-apex-muted" />
        <span className="text-xs text-apex-muted font-mono">{clock}</span>
      </div>
    </header>
  );
}
