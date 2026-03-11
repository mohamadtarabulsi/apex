const API_BASE = '/api/v1';

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  health: () => fetchJSON('/health'),
  status: () => fetchJSON(`${API_BASE}/status`),
  prices: (symbol: string, timeframe = '1H', limit = 100) =>
    fetchJSON(`/prices/${symbol}?timeframe=${timeframe}&limit=${limit}`),
  signals: (params?: { status?: string; strategy?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set('status', params.status);
    if (params?.strategy) qs.set('strategy', params.strategy);
    if (params?.limit) qs.set('limit', String(params.limit));
    return fetchJSON(`/signals?${qs}`);
  },
  signal: (id: string) => fetchJSON(`/signals/${id}`),
  portfolio: () => fetchJSON('/portfolio'),
  risk: () => fetchJSON('/risk'),
  calibration: () => fetchJSON('/calibration'),
  predictions: (params?: { platform?: string; resolved?: boolean }) => {
    const qs = new URLSearchParams();
    if (params?.platform) qs.set('platform', params.platform);
    if (params?.resolved !== undefined) qs.set('resolved', String(params.resolved));
    return fetchJSON(`/predictions?${qs}`);
  },
};
