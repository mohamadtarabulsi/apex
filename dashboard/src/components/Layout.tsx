import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { StatusBar } from './StatusBar';
import { OverviewPanel } from './OverviewPanel';
import { SignalFeed } from './SignalFeed';
import { SystemHealth } from './SystemHealth';
import { useAppStore } from '../stores/appStore';
import {
  BarChart3,
  Briefcase,
  ShieldAlert,
  Settings,
} from 'lucide-react';

function MarketsPage() {
  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-4 h-4 text-apex-blue" />
        <h2 className="text-sm text-apex-text uppercase tracking-wider">Markets</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {[
          { symbol: 'BTC-USD', price: '$67,482', change: '+2.34%', up: true },
          { symbol: 'ETH-USD', price: '$3,421', change: '-0.87%', up: false },
          { symbol: 'SOL-USD', price: '$142.80', change: '+5.12%', up: true },
          { symbol: 'SPY', price: '$512.30', change: '+0.42%', up: true },
          { symbol: 'QQQ', price: '$438.15', change: '+0.68%', up: true },
          { symbol: 'VIX', price: '14.20', change: '-3.21%', up: false },
        ].map((m) => (
          <div
            key={m.symbol}
            className="bg-apex-panel border border-apex-border rounded-lg p-4 hover:border-apex-muted/50 transition-colors"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold">{m.symbol}</span>
              <span
                className={`text-xs ${m.up ? 'text-apex-green' : 'text-apex-red'}`}
              >
                {m.change}
              </span>
            </div>
            <span className="text-lg font-bold text-apex-text">{m.price}</span>
          </div>
        ))}
      </div>
      <div className="mt-4 bg-apex-panel border border-apex-border rounded-lg p-6 flex items-center justify-center">
        <span className="text-xs text-apex-muted">
          Live market data feeds will activate in Phase 2
        </span>
      </div>
    </div>
  );
}

function PortfolioPage() {
  const { portfolioSummary } = useAppStore();
  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="flex items-center gap-2 mb-4">
        <Briefcase className="w-4 h-4 text-apex-green" />
        <h2 className="text-sm text-apex-text uppercase tracking-wider">Portfolio</h2>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        <div className="bg-apex-panel border border-apex-border rounded-lg p-4">
          <span className="text-[10px] text-apex-muted uppercase">Open Positions</span>
          <div className="text-xl font-bold text-apex-text mt-1">
            {portfolioSummary.open_positions}
          </div>
        </div>
        <div className="bg-apex-panel border border-apex-border rounded-lg p-4">
          <span className="text-[10px] text-apex-muted uppercase">Realized P&L</span>
          <div className="text-xl font-bold text-apex-green mt-1">
            ${portfolioSummary.total_realized_pnl.toFixed(2)}
          </div>
        </div>
        <div className="bg-apex-panel border border-apex-border rounded-lg p-4">
          <span className="text-[10px] text-apex-muted uppercase">Today's P&L</span>
          <div className="text-xl font-bold text-apex-text mt-1">$0.00</div>
        </div>
        <div className="bg-apex-panel border border-apex-border rounded-lg p-4">
          <span className="text-[10px] text-apex-muted uppercase">Capital</span>
          <div className="text-xl font-bold text-apex-blue mt-1">$10,000</div>
        </div>
      </div>
      <div className="bg-apex-panel border border-apex-border rounded-lg p-6 flex items-center justify-center">
        <span className="text-xs text-apex-muted">
          Trade history will populate as execution begins
        </span>
      </div>
    </div>
  );
}

function RiskPage() {
  const { risk } = useAppStore();
  const metrics = [
    { label: 'Portfolio Heat', value: risk?.portfolio_heat ?? 0, fmt: (v: number) => `${(v * 100).toFixed(1)}%` },
    { label: 'VaR (95%)', value: risk?.var_95 ?? 0, fmt: (v: number) => `$${v.toFixed(0)}` },
    { label: 'CVaR (95%)', value: risk?.cvar_95 ?? 0, fmt: (v: number) => `$${v.toFixed(0)}` },
    { label: 'Current Drawdown', value: risk?.current_drawdown ?? 0, fmt: (v: number) => `${(v * 100).toFixed(1)}%` },
    { label: 'Max Drawdown', value: risk?.max_drawdown ?? 0, fmt: (v: number) => `${(v * 100).toFixed(1)}%` },
    { label: 'Realized Vol', value: risk?.realized_vol ?? 0, fmt: (v: number) => `${(v * 100).toFixed(1)}%` },
    { label: 'Leverage', value: risk?.leverage ?? 0, fmt: (v: number) => `${v.toFixed(2)}x` },
    { label: 'Open Positions', value: risk?.open_positions ?? 0, fmt: (v: number) => String(v) },
  ];

  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="flex items-center gap-2 mb-4">
        <ShieldAlert className="w-4 h-4 text-apex-red" />
        <h2 className="text-sm text-apex-text uppercase tracking-wider">Risk Dashboard</h2>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        {metrics.map((m) => (
          <div key={m.label} className="bg-apex-panel border border-apex-border rounded-lg p-4">
            <span className="text-[10px] text-apex-muted uppercase">{m.label}</span>
            <div className="text-lg font-bold text-apex-text mt-1">{m.fmt(m.value)}</div>
          </div>
        ))}
      </div>
      <div className="bg-apex-panel border border-apex-border rounded-lg p-4">
        <h3 className="text-xs text-apex-muted uppercase tracking-wider mb-3">Kill Switch</h3>
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-apex-green pulse-dot" />
          <span className="text-sm text-apex-green">SYSTEM ACTIVE</span>
          <span className="text-[10px] text-apex-muted ml-auto">
            Kill switch will auto-trigger at 15% max drawdown
          </span>
        </div>
      </div>
    </div>
  );
}

function SettingsPage() {
  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="flex items-center gap-2 mb-4">
        <Settings className="w-4 h-4 text-apex-muted" />
        <h2 className="text-sm text-apex-text uppercase tracking-wider">Settings</h2>
      </div>
      <div className="space-y-3">
        {[
          { section: 'API Keys', desc: 'Configure broker and AI model API keys' },
          { section: 'Risk Limits', desc: 'Set max drawdown, position sizing, and kill switch thresholds' },
          { section: 'Strategies', desc: 'Enable/disable trading strategies and adjust parameters' },
          { section: 'Notifications', desc: 'Telegram alerts, email, and webhook configuration' },
          { section: 'Data Feeds', desc: 'Manage market data sources and WebSocket connections' },
        ].map((item) => (
          <div
            key={item.section}
            className="bg-apex-panel border border-apex-border rounded-lg p-4 hover:border-apex-muted/50 transition-colors cursor-pointer"
          >
            <span className="text-sm font-medium">{item.section}</span>
            <p className="text-[10px] text-apex-muted mt-1">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function SignalsPage() {
  const { signals } = useAppStore();
  return (
    <div className="h-full overflow-y-auto p-4">
      <SignalFeed signals={signals} />
    </div>
  );
}

export function Layout() {
  const { currentPage } = useAppStore();

  const renderPage = () => {
    switch (currentPage) {
      case 'overview':
        return <OverviewPanel />;
      case 'markets':
        return <MarketsPage />;
      case 'signals':
        return <SignalsPage />;
      case 'portfolio':
        return <PortfolioPage />;
      case 'risk':
        return <RiskPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <OverviewPanel />;
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-apex-bg scanline relative overflow-hidden">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-hidden">{renderPage()}</main>
      </div>
      <StatusBar />
    </div>
  );
}
