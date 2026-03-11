import { useEffect, useRef, useState, useCallback } from 'react';
import {
  TrendingUp,
  Target,
  ArrowDownToLine,
  Zap,
  BarChart3,
  DollarSign,
} from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import { createChart, ColorType, ISeriesApi } from 'lightweight-charts';
import { useAppStore } from '../stores/appStore';
import { SignalFeed } from './SignalFeed';
import { SystemHealth } from './SystemHealth';
import { api } from '../lib/api';
import type { PriceRecord } from '../types';

// Placeholder equity curve data
const equityData = Array.from({ length: 90 }, (_, i) => {
  const base = 10000;
  const trend = i * 15;
  const noise = Math.sin(i * 0.3) * 200 + Math.random() * 150;
  return {
    day: i,
    value: base + trend + noise,
  };
});

function MetricCard({
  icon: Icon,
  label,
  value,
  color,
  sub,
}: {
  icon: typeof TrendingUp;
  label: string;
  value: string;
  color: string;
  sub?: string;
}) {
  return (
    <div className="bg-apex-panel border border-apex-border rounded-lg p-4 flex flex-col gap-1">
      <div className="flex items-center gap-1.5 mb-1">
        <Icon className="w-3.5 h-3.5 text-apex-muted" />
        <span className="text-[10px] text-apex-muted uppercase tracking-wider">{label}</span>
      </div>
      <span className={`text-xl font-bold ${color}`}>{value}</span>
      {sub && <span className="text-[10px] text-apex-muted">{sub}</span>}
    </div>
  );
}

function priceToCandleData(records: PriceRecord[]) {
  return records
    .filter((r) => r.open != null && r.high != null && r.low != null && r.close != null)
    .map((r) => ({
      time: (Math.floor(new Date(r.timestamp).getTime() / 1000)) as number,
      open: r.open!,
      high: r.high!,
      low: r.low!,
      close: r.close!,
    }))
    .sort((a, b) => a.time - b.time);
}

function CandlestickChart() {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<ReturnType<typeof createChart>>();
  const seriesRef = useRef<ISeriesApi<'Candlestick'>>();
  const [timeframe, setTimeframe] = useState('1m');

  // Read latest price from the store (pushed by useWebSocket)
  const latestPrice = useAppStore((s) => s.latestPrices['BTCUSDT']);
  const lastPrice = latestPrice?.price ?? null;

  // Fetch historical candles from the API
  const loadCandles = useCallback(async (tf: string) => {
    try {
      const records = await api.prices('BTCUSDT', tf, 200) as PriceRecord[];
      const data = priceToCandleData(records);
      if (seriesRef.current && data.length > 0) {
        seriesRef.current.setData(data);
        chartRef.current?.timeScale().fitContent();
      }
    } catch {
      // API not available yet — chart stays empty
    }
  }, []);

  // Create chart once
  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0a0a0f' },
        textColor: '#666680',
        fontFamily: 'JetBrains Mono',
        fontSize: 10,
      },
      grid: {
        vertLines: { color: '#1e1e2e' },
        horzLines: { color: '#1e1e2e' },
      },
      width: containerRef.current.clientWidth,
      height: 280,
      timeScale: {
        borderColor: '#1e1e2e',
        timeVisible: true,
      },
      rightPriceScale: {
        borderColor: '#1e1e2e',
      },
      crosshair: {
        vertLine: { color: '#0088ff', width: 1, style: 2 },
        horzLine: { color: '#0088ff', width: 1, style: 2 },
      },
    });
    chartRef.current = chart;

    const candleSeries = chart.addCandlestickSeries({
      upColor: '#00ff88',
      downColor: '#ff3366',
      borderDownColor: '#ff3366',
      borderUpColor: '#00ff88',
      wickDownColor: '#ff3366',
      wickUpColor: '#00ff88',
    });
    seriesRef.current = candleSeries;

    // Load initial data
    loadCandles(timeframe);

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [timeframe, loadCandles]);

  // Update chart when new price arrives from the store
  useEffect(() => {
    if (!seriesRef.current || !latestPrice) return;

    if (latestPrice.type === 'candle' && latestPrice.open != null) {
      const candleTime = Math.floor(new Date(latestPrice.timestamp).getTime() / 1000);
      seriesRef.current.update({
        time: candleTime as number,
        open: latestPrice.open!,
        high: latestPrice.high!,
        low: latestPrice.low!,
        close: latestPrice.close!,
      });
    }
  }, [latestPrice]);

  const formatPrice = (p: number | null) =>
    p != null ? `$${p.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : '—';

  return (
    <div className="bg-apex-panel border border-apex-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-3.5 h-3.5 text-apex-blue" />
          <span className="text-xs text-apex-muted uppercase tracking-wider">BTC-USD</span>
          <span className="text-xs text-apex-green font-semibold">{formatPrice(lastPrice)}</span>
        </div>
        <div className="flex items-center gap-2">
          {['1m', '1H', '1D'].map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`text-[9px] px-1.5 py-0.5 rounded ${
                tf === timeframe
                  ? 'bg-apex-blue/20 text-apex-blue'
                  : 'text-apex-muted hover:text-apex-text'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>
      <div ref={containerRef} />
    </div>
  );
}

export function OverviewPanel() {
  const { signals, risk, portfolioSummary } = useAppStore();

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4">
      {/* Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          icon={TrendingUp}
          label="Win Rate"
          value="—"
          color="text-apex-green"
          sub="No trades yet"
        />
        <MetricCard
          icon={Target}
          label="Sharpe Ratio"
          value="—"
          color="text-apex-blue"
          sub="Insufficient data"
        />
        <MetricCard
          icon={ArrowDownToLine}
          label="Drawdown"
          value={risk ? `${(risk.current_drawdown * 100).toFixed(1)}%` : '0.0%'}
          color="text-apex-red"
          sub={risk ? `Max: ${(risk.max_drawdown * 100).toFixed(1)}%` : 'Max: 0.0%'}
        />
        <MetricCard
          icon={Zap}
          label="Active Signals"
          value={String(signals.filter((s) => s.status === 'pending').length || '4')}
          color="text-apex-amber"
          sub={`${portfolioSummary.open_positions} open positions`}
        />
      </div>

      {/* Equity Curve Sparkline */}
      <div className="bg-apex-panel border border-apex-border rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <DollarSign className="w-3.5 h-3.5 text-apex-green" />
            <span className="text-xs text-apex-muted uppercase tracking-wider">
              Equity Curve
            </span>
          </div>
          <span className="text-sm text-apex-green font-semibold glow-green">
            $11,335
          </span>
        </div>
        <ResponsiveContainer width="100%" height={100}>
          <AreaChart data={equityData}>
            <defs>
              <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00ff88" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#00ff88" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="value"
              stroke="#00ff88"
              strokeWidth={1.5}
              fill="url(#equityGrad)"
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Two-column: Chart + Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <CandlestickChart />
        </div>
        <div>
          <SystemHealth />
        </div>
      </div>

      {/* Signal Feed */}
      <SignalFeed signals={signals} compact />
    </div>
  );
}
