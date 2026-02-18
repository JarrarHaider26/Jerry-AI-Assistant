/**
 * Jerry System Monitor Service
 * Handles real-time system stats polling from the Python bridge,
 * proactive alerts, and performance tracking.
 */

export interface SystemSnapshot {
  cpu: {
    percent: number;
    cores: number;
    freq_current: number;
    freq_max: number;
    per_core: number[];
  };
  memory: {
    percent: number;
    total_gb: number;
    used_gb: number;
    available_gb: number;
  };
  disk: {
    percent: number;
    total_gb: number;
    used_gb: number;
    free_gb: number;
  };
  network: {
    bytes_sent: number;
    bytes_recv: number;
    sent_mb: number;
    recv_mb: number;
  };
  battery: {
    percent: number | null;
    charging: boolean | null;
    time_left: string;
  };
  uptime: string;
  os: string;
  hostname: string;
  temperatures?: Record<string, Array<{ label: string; current: number }>>;
}

export interface AlertRule {
  id: string;
  metric: 'cpu' | 'memory' | 'disk' | 'battery';
  threshold: number;
  direction: 'above' | 'below';
  message: string;
  cooldownMs: number;
  lastTriggered: number;
  enabled: boolean;
}

type AlertCallback = (rule: AlertRule, value: number) => void;

export class SystemMonitorService {
  private history: SystemSnapshot[] = [];
  private maxHistory: number = 120; // ~10 minutes at 5s intervals
  private alertRules: AlertRule[] = [];
  private alertCallback: AlertCallback | null = null;
  private lastSnapshot: SystemSnapshot | null = null;
  private cache = new Map<string, { value: any; timestamp: number }>();
  private cacheTtlMs = 5000;

  constructor() {
    this.setupDefaultAlerts();
  }

  /**
   * Set up default alert thresholds.
   */
  private setupDefaultAlerts(): void {
    this.alertRules = [
      {
        id: 'cpu_high',
        metric: 'cpu',
        threshold: 90,
        direction: 'above',
        message: 'CPU usage critical: {value}%',
        cooldownMs: 60000,
        lastTriggered: 0,
        enabled: true
      },
      {
        id: 'memory_high',
        metric: 'memory',
        threshold: 85,
        direction: 'above',
        message: 'Memory usage high: {value}%',
        cooldownMs: 60000,
        lastTriggered: 0,
        enabled: true
      },
      {
        id: 'disk_high',
        metric: 'disk',
        threshold: 90,
        direction: 'above',
        message: 'Disk usage critical: {value}%',
        cooldownMs: 300000,
        lastTriggered: 0,
        enabled: true
      },
      {
        id: 'battery_low',
        metric: 'battery',
        threshold: 15,
        direction: 'below',
        message: 'Battery critically low: {value}%',
        cooldownMs: 120000,
        lastTriggered: 0,
        enabled: true
      }
    ];
  }

  /**
   * Register a callback for alerts.
   */
  public onAlert(callback: AlertCallback): void {
    this.alertCallback = callback;
  }

  /**
   * Process an incoming system snapshot from the bridge.
   */
  public processSnapshot(snapshot: SystemSnapshot): void {
    this.lastSnapshot = snapshot;
    this.history.push(snapshot);
    if (this.history.length > this.maxHistory) {
      this.history.shift();
    }
    this.cache.clear();
    this.checkAlerts(snapshot);
  }

  /**
   * Check alert rules against a snapshot.
   */
  private checkAlerts(snapshot: SystemSnapshot): void {
    if (!this.alertCallback) return;
    
    const now = Date.now();
    
    for (const rule of this.alertRules) {
      if (!rule.enabled) continue;
      if (now - rule.lastTriggered < rule.cooldownMs) continue;

      let value: number | null = null;
      
      switch (rule.metric) {
        case 'cpu': value = snapshot.cpu.percent; break;
        case 'memory': value = snapshot.memory.percent; break;
        case 'disk': value = snapshot.disk.percent; break;
        case 'battery': value = snapshot.battery.percent; break;
      }

      if (value === null) continue;

      const triggered = rule.direction === 'above' 
        ? value > rule.threshold 
        : value < rule.threshold;

      if (triggered) {
        rule.lastTriggered = now;
        this.alertCallback(rule, value);
      }
    }
  }

  /**
   * Get the latest snapshot.
   */
  public getLatest(): SystemSnapshot | null {
    const cached = this.getCached<SystemSnapshot | null>('latest');
    if (cached !== null) return cached;
    const current = this.lastSnapshot;
    this.setCache('latest', current);
    return current;
  }

  /**
   * Get historical data for a metric.
   */
  public getHistory(metric: 'cpu' | 'memory' | 'disk' | 'battery', count?: number): number[] {
    const data = this.history.slice(-(count || this.maxHistory));
    return data.map(s => {
      switch (metric) {
        case 'cpu': return s.cpu.percent;
        case 'memory': return s.memory.percent;
        case 'disk': return s.disk.percent;
        case 'battery': return s.battery.percent || 0;
        default: return 0;
      }
    });
  }

  /**
   * Get average metrics over the history window.
   */
  public getAverages(): { cpu: number; memory: number; disk: number } {
    if (this.history.length === 0) return { cpu: 0, memory: 0, disk: 0 };
    
    const sum = this.history.reduce((acc, s) => ({
      cpu: acc.cpu + s.cpu.percent,
      memory: acc.memory + s.memory.percent,
      disk: acc.disk + s.disk.percent
    }), { cpu: 0, memory: 0, disk: 0 });

    const len = this.history.length;
    return {
      cpu: Math.round(sum.cpu / len * 10) / 10,
      memory: Math.round(sum.memory / len * 10) / 10,
      disk: Math.round(sum.disk / len * 10) / 10
    };
  }

  /**
   * Get a formatted status report for Jerry to speak.
   */
  public getStatusReport(): string {
    const cached = this.getCached<string>('status_report');
    if (cached) return cached;
    if (!this.lastSnapshot) return 'System monitoring not yet initialized.';
    
    const s = this.lastSnapshot;
    const parts: string[] = [];
    parts.push(`CPU at ${s.cpu.percent}%`);
    parts.push(`Memory at ${s.memory.percent}% (${s.memory.used_gb}GB of ${s.memory.total_gb}GB)`);
    parts.push(`Disk at ${s.disk.percent}% (${s.disk.free_gb}GB free)`);
    
    if (s.battery.percent !== null) {
      parts.push(`Battery at ${s.battery.percent}%${s.battery.charging ? ', charging' : ''}`);
    }
    
    parts.push(`Uptime: ${s.uptime}`);
    
    const report = parts.join('. ');
    this.setCache('status_report', report);
    return report;
  }

  private getCached<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;
    if (Date.now() - cached.timestamp > this.cacheTtlMs) return null;
    return cached.value as T;
  }

  private setCache(key: string, value: any): void {
    this.cache.set(key, { value, timestamp: Date.now() });
  }

  /**
   * Add a custom alert rule.
   */
  public addAlert(rule: Omit<AlertRule, 'id' | 'lastTriggered'>): void {
    this.alertRules.push({
      ...rule,
      id: `custom_${Date.now()}`,
      lastTriggered: 0
    });
  }

  /**
   * Get all alert rules.
   */
  public getAlertRules(): AlertRule[] {
    return [...this.alertRules];
  }
}
