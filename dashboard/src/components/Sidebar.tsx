import {
  LayoutDashboard,
  BarChart3,
  Zap,
  Briefcase,
  ShieldAlert,
  Settings,
} from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import type { NavPage } from '../types';

const navItems: { page: NavPage; icon: typeof LayoutDashboard; label: string }[] = [
  { page: 'overview', icon: LayoutDashboard, label: 'Overview' },
  { page: 'markets', icon: BarChart3, label: 'Markets' },
  { page: 'signals', icon: Zap, label: 'Signals' },
  { page: 'portfolio', icon: Briefcase, label: 'Portfolio' },
  { page: 'risk', icon: ShieldAlert, label: 'Risk' },
  { page: 'settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const { currentPage, setPage, sidebarExpanded, setSidebarExpanded } = useAppStore();

  return (
    <nav
      className="h-full bg-apex-panel border-r border-apex-border flex flex-col py-3 transition-all duration-200 shrink-0"
      style={{ width: sidebarExpanded ? 160 : 52 }}
      onMouseEnter={() => setSidebarExpanded(true)}
      onMouseLeave={() => setSidebarExpanded(false)}
    >
      {navItems.map(({ page, icon: Icon, label }) => {
        const active = currentPage === page;
        return (
          <button
            key={page}
            onClick={() => setPage(page)}
            className={`
              flex items-center gap-3 px-3.5 py-2.5 mx-1 rounded-md transition-colors
              ${active
                ? 'bg-apex-green/10 text-apex-green'
                : 'text-apex-muted hover:text-apex-text hover:bg-white/5'
              }
            `}
          >
            <Icon className="w-4.5 h-4.5 shrink-0" style={{ width: 18, height: 18 }} />
            {sidebarExpanded && (
              <span className="text-xs font-medium whitespace-nowrap">{label}</span>
            )}
          </button>
        );
      })}
    </nav>
  );
}
