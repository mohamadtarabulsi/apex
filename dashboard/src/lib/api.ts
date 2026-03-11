const API_BASE = '/api/v1';

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  // System-level (no module prefix)
  health: () => fetch('/health').then((r) => r.json()),
  status: () => fetchJSON('/status'),

  // Data Engine — /api/v1/data/*
  prices: (symbol: string, timeframe = '1H', limit = 100) =>
    fetchJSON(`/data/prices/${symbol}?timeframe=${timeframe}&limit=${limit}`),

  // Strategy Engine — /api/v1/strategy/*
  signals: (params?: { status?: string; strategy?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set('status', params.status);
    if (params?.strategy) qs.set('strategy', params.strategy);
    if (params?.limit) qs.set('limit', String(params.limit));
    return fetchJSON(`/strategy/signals?${qs}`);
  },
  signal: (id: string) => fetchJSON(`/strategy/signals/${id}`),
  predictions: (params?: { platform?: string; resolved?: boolean }) => {
    const qs = new URLSearchParams();
    if (params?.platform) qs.set('platform', params.platform);
    if (params?.resolved !== undefined) qs.set('resolved', String(params.resolved));
    return fetchJSON(`/strategy/predictions?${qs}`);
  },

  // Risk & Execution Engine — /api/v1/risk/*
  portfolio: () => fetchJSON('/risk/portfolio'),
  risk: () => fetchJSON('/risk/state'),

  // Intelligence Engine — /api/v1/intelligence/*
  calibration: () => fetchJSON('/intelligence/calibration'),
};
