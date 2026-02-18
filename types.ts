
export enum JerryStatus {
  SLEEPING = 'SLEEPING',
  LISTENING = 'LISTENING',
  THINKING = 'THINKING',
  SPEAKING = 'SPEAKING',
  EXECUTING = 'EXECUTING',
  WORKFLOW = 'WORKFLOW'
}

export interface LogEntry {
  id: string;
  timestamp: string;
  source: 'SYSTEM' | 'USER' | 'JERRY' | 'BRIDGE' | 'WORKFLOW';
  message: string;
  type?: 'info' | 'error' | 'success' | 'command' | 'warning' | 'alert';
}

export interface SystemStats {
  cpu: number;
  memory: number;
  disk: number;
  network: string;
  uptime: string;
  battery: number | null;
  batteryCharging: boolean | null;
  hostname: string;
  os: string;
  cpuCores: number;
  cpuFreq: number;
  memoryTotal: number;
  memoryUsed: number;
  diskTotal: number;
  diskFree: number;
  networkSent: number;
  networkRecv: number;
}

export interface ToolCall {
  name: string;
  args: any;
  id: string;
}

export interface BridgeCommand {
  action: string;
  target?: string;
  payload?: string;
  extra?: string;
  auth_token?: string;
}

export interface BridgeResponse {
  status: 'success' | 'error' | 'warning' | 'info';
  message: string;
  [key: string]: any;
}

export const DEFAULT_STATS: SystemStats = {
  cpu: 0,
  memory: 0,
  disk: 0,
  network: 'OFFLINE',
  uptime: '00:00:00',
  battery: null,
  batteryCharging: null,
  hostname: '',
  os: '',
  cpuCores: 0,
  cpuFreq: 0,
  memoryTotal: 0,
  memoryUsed: 0,
  diskTotal: 0,
  diskFree: 0,
  networkSent: 0,
  networkRecv: 0,
};
