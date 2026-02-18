/**
 * Jerry Security Service
 * Handles API key encryption, bridge authentication, command validation, and activity logging.
 */

// --- Bridge Authentication ---
export class BridgeAuthenticator {
  private token: string;

  constructor(token?: string) {
    const envToken = (import.meta as any).env?.VITE_JERRY_BRIDGE_TOKEN as string | undefined;
    if (!token && !envToken) {
      throw new Error('CRITICAL: VITE_JERRY_BRIDGE_TOKEN must be set in .env.local');
    }

    this.token = token || envToken!;

    try {
      sessionStorage.setItem('jerry_bridge_token', this.token);
    } catch (e) {
      console.warn('Failed to store token in sessionStorage');
    }
  }

  /**
   * Wraps a command payload with auth token.
   */
  public wrapCommand(command: Record<string, any>): Record<string, any> {
    const nonce = BridgeAuthenticator.generateNonce();
    return {
      ...command,
      auth_token: this.token,
      timestamp: Date.now(),
      nonce
    };
  }

  /**
   * Generate a session token.
   */
  public getToken(): string {
    return this.token;
  }

  private static generateNonce(): string {
    const bytes = new Uint8Array(16);
    if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
      crypto.getRandomValues(bytes);
    } else {
      for (let i = 0; i < bytes.length; i++) bytes[i] = Math.floor(Math.random() * 256);
    }
    return Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
  }
}

// --- Command Validator ---
export class CommandValidator {
  private static DANGEROUS_ACTIONS = new Set([
    'shutdown', 'restart', 'delete_file', 'delete_folder', 
    'format', 'kill_process', 'shell_execute', 'logoff'
  ]);

  private static BLOCKED_PATTERNS = [
    'format c:', 'rm -rf /', 'del /s /q c:', 'rd /s /q c:',
    'reg delete hklm', 'reg delete hkcu'
  ];

  /**
   * Check if a command requires confirmation before execution.
   */
  public static requiresConfirmation(action: string, target?: string, payload?: string): boolean {
    if (this.DANGEROUS_ACTIONS.has(action.toLowerCase())) return true;
    
    const combined = `${action} ${target || ''} ${payload || ''}`.toLowerCase();
    return this.BLOCKED_PATTERNS.some(p => combined.includes(p));
  }

  /**
   * Validate a command before execution.
   */
  public static validate(command: Record<string, any>): { valid: boolean; message: string; dangerous: boolean } {
    const action = (command.action || '').toLowerCase();
    const target = (command.target || '').toLowerCase();
    const payload = (command.payload || '').toLowerCase();
    
    // Check blocked commands
    const combined = `${action} ${target} ${payload}`;
    for (const blocked of this.BLOCKED_PATTERNS) {
      if (combined.includes(blocked)) {
        return { valid: false, message: `BLOCKED: '${blocked}' is a prohibited operation.`, dangerous: true };
      }
    }

    // Check required fields
    if (!action) {
      return { valid: false, message: 'Missing action field.', dangerous: false };
    }

    return { 
      valid: true, 
      message: 'OK', 
      dangerous: this.DANGEROUS_ACTIONS.has(action) 
    };
  }
}

// --- Activity Logger ---
export interface ActivityLog {
  id: string;
  timestamp: string;
  action: string;
  target?: string;
  source: 'voice' | 'manual' | 'automation' | 'system';
  status: 'success' | 'failed' | 'pending' | 'blocked';
  details?: string;
}

export class ActivityLogger {
  private logs: ActivityLog[] = [];
  private maxLogs: number = 1000;

  public log(
    action: string, 
    target: string = '', 
    source: ActivityLog['source'] = 'voice',
    status: ActivityLog['status'] = 'success',
    details?: string
  ): ActivityLog {
    const entry: ActivityLog = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      action,
      target,
      source,
      status,
      details
    };
    this.logs.push(entry);
    if (this.logs.length > this.maxLogs) this.logs.shift();
    return entry;
  }

  public getRecent(count: number = 20): ActivityLog[] {
    return this.logs.slice(-count);
  }

  public getByAction(action: string): ActivityLog[] {
    return this.logs.filter(l => l.action === action);
  }

  public getFailures(): ActivityLog[] {
    return this.logs.filter(l => l.status === 'failed');
  }

  public clear(): void {
    this.logs = [];
  }

  public getStats() {
    const total = this.logs.length;
    const successful = this.logs.filter(l => l.status === 'success').length;
    const failed = this.logs.filter(l => l.status === 'failed').length;
    return {
      total,
      successful,
      failed,
      successRate: total > 0 ? Math.round((successful / total) * 100) : 100
    };
  }

  private generateId(): string {
    return `log_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
  }
}
