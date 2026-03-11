export interface PriceRecord {
  id: number;
  symbol: string;
  asset_class: string;
  exchange: string | null;
  timestamp: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
  timeframe: string | null;
  indicators: Record<string, number> | null;
  created_at: string | null;
}

export interface SignalRecord {
  id: number;
  signal_id: string;
  symbol: string;
  asset_class: string;
  strategy: string;
  direction: 'long' | 'short';
  confidence: number;
  risk_reward: number | null;
  entry_price: number | null;
  stop_loss: number | null;
  take_profit: number | null;
  reasoning: string | null;
  regime_state: string | null;
  factors: Record<string, number> | null;
  status: 'pending' | 'approved' | 'rejected' | 'executed' | 'expired';
  timestamp: string;
  created_at: string | null;
}

export interface RiskState {
  portfolio_heat: number;
  var_95: number;
  cvar_95: number;
  current_drawdown: number;
  max_drawdown: number;
  realized_vol: number;
  target_vol: number;
  leverage: number;
  open_positions: number;
  daily_pnl: number;
  weekly_pnl: number;
  risk_limits: Record<string, unknown> | null;
  timestamp: string;
}

export interface TradeRecord {
  id: number;
  trade_id: string;
  signal_id: string | null;
  symbol: string;
  asset_class: string;
  broker: string;
  direction: 'long' | 'short';
  quantity: number;
  entry_price: number | null;
  exit_price: number | null;
  pnl: number | null;
  pnl_pct: number | null;
  status: 'open' | 'closed' | 'cancelled';
  strategy: string | null;
  created_at: string | null;
}

export interface ServiceStatus {
  service: string;
  status: string;
  details?: Record<string, unknown>;
}

export interface HealthResponse {
  status: string;
  uptime_seconds: number;
  services: Record<string, ServiceStatus>;
}

export interface WSMessage {
  type: 'status' | 'price' | 'signal' | 'risk' | 'pong';
  data: unknown;
}

export type NavPage = 'overview' | 'markets' | 'signals' | 'portfolio' | 'risk' | 'settings';
