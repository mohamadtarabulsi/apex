import { useAppStore } from '../stores/appStore';

export function StatusBar() {
  const { connected, uptime } = useAppStore();

  const feeds = [
    { name: 'Binance WS', active: false },
    { name: 'Alpaca WS', active: false },
    { name: 'Kalshi REST', active: false },
    { name: 'Polymarket REST', active: false },
    { name: 'NATS Bus', active: connected },
    { name: 'Redis Stream', active: connected },
  ];

  const formatUptime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h}h ${m}m ${s}s`;
  };

  return (
    <footer className="h-7 bg-apex-panel border-t border-apex-border flex items-center justify-between px-4 shrink-0">
      <div className="flex items-center gap-4">
        {feeds.map((feed) => (
          <div key={feed.name} className="flex items-center gap-1.5">
            <div
              className={`w-1.5 h-1.5 rounded-full ${
                feed.active ? 'bg-apex-green' : 'bg-apex-muted'
              }`}
            />
            <span className="text-[9px] text-apex-muted uppercase tracking-wide">
              {feed.name}
            </span>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <span className="text-[9px] text-apex-muted">
          UPTIME: {formatUptime(uptime)}
        </span>
        <span className="text-[9px] text-apex-muted">
          ENV: DEV
        </span>
        <span className={`text-[9px] ${connected ? 'text-apex-green' : 'text-apex-red'}`}>
          {connected ? '● CONNECTED' : '○ DISCONNECTED'}
        </span>
      </div>
    </footer>
  );
}
