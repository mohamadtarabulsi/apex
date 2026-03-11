import { create } from 'zustand';
import type { SignalRecord, RiskState, ServiceStatus, NavPage } from '../types';

interface AppState {
  // Navigation
  currentPage: NavPage;
  sidebarExpanded: boolean;
  setPage: (page: NavPage) => void;
  setSidebarExpanded: (expanded: boolean) => void;

  // System
  connected: boolean;
  uptime: number;
  services: Record<string, ServiceStatus>;
  setConnected: (c: boolean) => void;
  setUptime: (u: number) => void;
  setServices: (s: Record<string, ServiceStatus>) => void;

  // Signals
  signals: SignalRecord[];
  setSignals: (s: SignalRecord[]) => void;
  addSignal: (s: SignalRecord) => void;

  // Risk
  risk: RiskState | null;
  setRisk: (r: RiskState) => void;

  // Portfolio
  portfolioSummary: { open_positions: number; total_realized_pnl: number };
  setPortfolioSummary: (p: { open_positions: number; total_realized_pnl: number }) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Navigation
  currentPage: 'overview',
  sidebarExpanded: false,
  setPage: (page) => set({ currentPage: page }),
  setSidebarExpanded: (expanded) => set({ sidebarExpanded: expanded }),

  // System
  connected: false,
  uptime: 0,
  services: {},
  setConnected: (connected) => set({ connected }),
  setUptime: (uptime) => set({ uptime }),
  setServices: (services) => set({ services }),

  // Signals
  signals: [],
  setSignals: (signals) => set({ signals }),
  addSignal: (signal) => set((state) => ({ signals: [signal, ...state.signals].slice(0, 100) })),

  // Risk
  risk: null,
  setRisk: (risk) => set({ risk }),

  // Portfolio
  portfolioSummary: { open_positions: 0, total_realized_pnl: 0 },
  setPortfolioSummary: (portfolioSummary) => set({ portfolioSummary }),
}));
