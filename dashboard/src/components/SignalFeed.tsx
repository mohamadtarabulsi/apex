import { ArrowUpRight, ArrowDownRight, Zap } from 'lucide-react';
import type { SignalRecord } from '../types';

// Demo signals to show while the system has no live data
const demoSignals: SignalRecord[] = [
  {
    id: 1,
    signal_id: 'demo-001',
    symbol: 'BTC-USD',
    asset_class: 'crypto',
    strategy: 'crypto_momentum',
    direction: 'long',
    confidence: 0.82,
    risk_reward: 2.4,
    entry_price: 67250.0,
    stop_loss: 65800.0,
    take_profit: 70700.0,
    reasoning: 'Strong momentum breakout above 20-day EMA with rising volume',
    regime_state: 'bull',
    factors: null,
    status: 'pending',
    timestamp: new Date().toISOString(),
    created_at: new Date().toISOString(),
  },
  {
    id: 2,
    signal_id: 'demo-002',
    symbol: 'KXHIGHNY',
    asset_class: 'prediction',
    strategy: 'weather_bot',
    direction: 'long',
    confidence: 0.74,
    risk_reward: 1.8,
    entry_price: 0.62,
    stop_loss: null,
    take_profit: null,
    reasoning: 'GFS ensemble shows 78% probability for high temp > 52°F, market at 62¢',
    regime_state: null,
    factors: null,
    status: 'approved',
    timestamp: new Date(Date.now() - 300000).toISOString(),
    created_at: new Date(Date.now() - 300000).toISOString(),
  },
  {
    id: 3,
    signal_id: 'demo-003',
    symbol: 'ETH-USD',
    asset_class: 'crypto',
    strategy: 'crypto_momentum',
    direction: 'short',
    confidence: 0.65,
    risk_reward: 1.5,
    entry_price: 3420.0,
    stop_loss: 3520.0,
    take_profit: 3270.0,
    reasoning: 'Bearish divergence on RSI with declining volume near resistance',
    regime_state: 'sideways',
    factors: null,
    status: 'executed',
    timestamp: new Date(Date.now() - 900000).toISOString(),
    created_at: new Date(Date.now() - 900000).toISOString(),
  },
  {
    id: 4,
    signal_id: 'demo-004',
    symbol: 'POLYMARKET-ELECTION',
    asset_class: 'prediction',
    strategy: 'prediction_arb',
    direction: 'long',
    confidence: 0.71,
    risk_reward: 3.2,
    entry_price: 0.45,
    stop_loss: null,
    take_profit: null,
    reasoning: 'Model ensemble predicts 68% vs market 45% — significant edge detected',
    regime_state: null,
    factors: null,
    status: 'pending',
    timestamp: new Date(Date.now() - 1800000).toISOString(),
    created_at: new Date(Date.now() - 1800000).toISOString(),
  },
];

const statusColors: Record<string, string> = {
  pending: 'text-apex-amber bg-apex-amber/10 border-apex-amber/30',
  approved: 'text-apex-blue bg-apex-blue/10 border-apex-blue/30',
  executed: 'text-apex-green bg-apex-green/10 border-apex-green/30',
  rejected: 'text-apex-red bg-apex-red/10 border-apex-red/30',
  expired: 'text-apex-muted bg-apex-muted/10 border-apex-muted/30',
};

interface SignalFeedProps {
  signals?: SignalRecord[];
  compact?: boolean;
}

export function SignalFeed({ signals, compact = false }: SignalFeedProps) {
  const displaySignals = signals?.length ? signals : demoSignals;

  return (
    <div className="bg-apex-panel border border-apex-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs text-apex-muted uppercase tracking-wider flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5" />
          Signal Feed
        </h3>
        <span className="text-[10px] text-apex-muted">
          {displaySignals.length} signals
        </span>
      </div>

      <div className={`space-y-2 ${compact ? 'max-h-64' : 'max-h-[500px]'} overflow-y-auto pr-1`}>
        {displaySignals.map((signal) => (
          <div
            key={signal.signal_id}
            className="bg-apex-bg/60 border border-apex-border rounded-md p-3 hover:border-apex-muted/50 transition-colors"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                {signal.direction === 'long' ? (
                  <ArrowUpRight className="w-4 h-4 text-apex-green" />
                ) : (
                  <ArrowDownRight className="w-4 h-4 text-apex-red" />
                )}
                <span className="text-sm font-semibold">{signal.symbol}</span>
                <span className="text-[10px] text-apex-muted uppercase">
                  {signal.asset_class}
                </span>
              </div>
              <span
                className={`text-[9px] uppercase px-1.5 py-0.5 rounded border ${
                  statusColors[signal.status] || statusColors.pending
                }`}
              >
                {signal.status}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2 text-[10px] mb-2">
              <div>
                <span className="text-apex-muted">Confidence</span>
                <div className={`font-semibold ${signal.confidence > 0.7 ? 'text-apex-green' : 'text-apex-amber'}`}>
                  {(signal.confidence * 100).toFixed(0)}%
                </div>
              </div>
              {signal.risk_reward && (
                <div>
                  <span className="text-apex-muted">R:R</span>
                  <div className="text-apex-blue font-semibold">
                    {signal.risk_reward.toFixed(1)}x
                  </div>
                </div>
              )}
              <div>
                <span className="text-apex-muted">Strategy</span>
                <div className="text-apex-text truncate">{signal.strategy}</div>
              </div>
            </div>

            {!compact && signal.reasoning && (
              <p className="text-[10px] text-apex-muted leading-relaxed line-clamp-2">
                {signal.reasoning}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
