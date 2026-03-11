import { Server, Database, Radio, HardDrive } from 'lucide-react';
import { useAppStore } from '../stores/appStore';

const serviceIcons: Record<string, typeof Server> = {
  postgres: Database,
  redis: HardDrive,
  nats: Radio,
  questdb: Server,
};

export function SystemHealth() {
  const { services } = useAppStore();

  const serviceList = ['postgres', 'redis', 'nats', 'questdb'];

  return (
    <div className="bg-apex-panel border border-apex-border rounded-lg p-4">
      <h3 className="text-xs text-apex-muted uppercase tracking-wider mb-3">
        Infrastructure Health
      </h3>
      <div className="space-y-2">
        {serviceList.map((name) => {
          const svc = services[name];
          const healthy = svc?.status === 'healthy';
          const Icon = serviceIcons[name] || Server;

          return (
            <div
              key={name}
              className="flex items-center justify-between py-1.5 px-2 rounded bg-apex-bg/50"
            >
              <div className="flex items-center gap-2">
                <Icon className="w-3.5 h-3.5 text-apex-muted" />
                <span className="text-xs uppercase">{name}</span>
              </div>
              <div className="flex items-center gap-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    healthy ? 'bg-apex-green pulse-dot' : 'bg-apex-red'
                  }`}
                />
                <span
                  className={`text-[10px] uppercase ${
                    healthy ? 'text-apex-green' : 'text-apex-red'
                  }`}
                >
                  {healthy ? 'healthy' : 'down'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
