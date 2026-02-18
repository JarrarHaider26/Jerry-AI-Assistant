/**
 * Jerry Workflow Engine Service
 * Enables multi-step automation sequences, conditional logic, 
 * time-based triggers, and cross-application workflows.
 */

export interface WorkflowStep {
  id: string;
  action: string;
  target?: string;
  payload?: string;
  extra?: string;
  delayMs?: number;         // Delay before executing this step
  condition?: {             // Conditional execution
    type: 'bridge_active' | 'time_after' | 'time_before' | 'always';
    value?: string;
  };
  onFailure?: 'skip' | 'abort' | 'retry';
  retries?: number;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  trigger: 'manual' | 'voice' | 'schedule' | 'event';
  schedule?: {
    type: 'once' | 'daily' | 'interval';
    time?: string;           // HH:MM for daily
    intervalMs?: number;     // For interval
    nextRun?: number;
  };
  enabled: boolean;
  lastRun?: string;
  runCount: number;
}

export interface WorkflowResult {
  workflowId: string;
  workflowName: string;
  startedAt: string;
  completedAt: string;
  steps: Array<{
    stepId: string;
    action: string;
    status: 'success' | 'failed' | 'skipped';
    result?: string;
    duration: number;
  }>;
  status: 'completed' | 'partial' | 'failed';
}

type CommandExecutor = (command: Record<string, any>) => Promise<any>;

export class WorkflowEngine {
  private workflows: Map<string, Workflow> = new Map();
  private executor: CommandExecutor | null = null;
  private schedulerInterval: ReturnType<typeof setInterval> | null = null;
  private onLogCallback: ((message: string, type: string) => void) | null = null;

  constructor() {
    this.loadBuiltInWorkflows();
  }

  /**
   * Set the command executor (sends commands to bridge).
   */
  public setExecutor(executor: CommandExecutor): void {
    this.executor = executor;
  }

  /**
   * Set logging callback.
   */
  public onLog(callback: (message: string, type: string) => void): void {
    this.onLogCallback = callback;
  }

  private log(message: string, type: string = 'info'): void {
    if (this.onLogCallback) this.onLogCallback(message, type);
  }

  /**
   * Load pre-built workflow templates.
   */
  private loadBuiltInWorkflows(): void {
    const builtIns: Workflow[] = [
      {
        id: 'wf_morning_routine',
        name: 'Morning Mode',
        description: 'Opens your morning apps, sets brightness to 70%, plays music',
        steps: [
          { id: 's1', action: 'brightness_control', target: 'set', payload: '70', delayMs: 0, onFailure: 'skip' },
          { id: 's2', action: 'open_app', target: 'chrome', delayMs: 1000, onFailure: 'skip' },
          { id: 's3', action: 'open_app', target: 'whatsapp', delayMs: 2000, onFailure: 'skip' },
          { id: 's4', action: 'open_app', target: 'spotify', delayMs: 3000, onFailure: 'skip' },
          { id: 's5', action: 'volume_control', target: 'set', payload: '40', delayMs: 1000, onFailure: 'skip' },
        ],
        trigger: 'voice',
        enabled: true,
        runCount: 0
      },
      {
        id: 'wf_work_mode',
        name: 'Work Mode',
        description: 'Opens dev tools, closes distractions, sets DnD',
        steps: [
          { id: 's1', action: 'close_app', target: 'spotify', delayMs: 0, onFailure: 'skip' },
          { id: 's2', action: 'close_app', target: 'whatsapp', delayMs: 500, onFailure: 'skip' },
          { id: 's3', action: 'close_app', target: 'discord', delayMs: 500, onFailure: 'skip' },
          { id: 's4', action: 'open_app', target: 'vscode', delayMs: 1000, onFailure: 'skip' },
          { id: 's5', action: 'open_app', target: 'chrome', delayMs: 2000, onFailure: 'skip' },
          { id: 's6', action: 'brightness_control', target: 'set', payload: '60', delayMs: 500, onFailure: 'skip' },
        ],
        trigger: 'voice',
        enabled: true,
        runCount: 0
      },
      {
        id: 'wf_night_mode',
        name: 'Night Mode',
        description: 'Dims screen, lowers volume, closes work apps',
        steps: [
          { id: 's1', action: 'brightness_control', target: 'set', payload: '20', delayMs: 0, onFailure: 'skip' },
          { id: 's2', action: 'volume_control', target: 'set', payload: '20', delayMs: 500, onFailure: 'skip' },
          { id: 's3', action: 'close_app', target: 'vscode', delayMs: 1000, onFailure: 'skip' },
          { id: 's4', action: 'close_app', target: 'teams', delayMs: 500, onFailure: 'skip' },
        ],
        trigger: 'voice',
        enabled: true,
        runCount: 0
      },
      {
        id: 'wf_gaming_mode',
        name: 'Gaming Mode',
        description: 'Closes background apps, maximizes performance',
        steps: [
          { id: 's1', action: 'close_app', target: 'chrome', delayMs: 0, onFailure: 'skip' },
          { id: 's2', action: 'close_app', target: 'vscode', delayMs: 500, onFailure: 'skip' },
          { id: 's3', action: 'close_app', target: 'teams', delayMs: 500, onFailure: 'skip' },
          { id: 's4', action: 'close_app', target: 'slack', delayMs: 500, onFailure: 'skip' },
          { id: 's5', action: 'open_app', target: 'steam', delayMs: 1000, onFailure: 'skip' },
          { id: 's6', action: 'brightness_control', target: 'set', payload: '80', delayMs: 500, onFailure: 'skip' },
          { id: 's7', action: 'volume_control', target: 'set', payload: '70', delayMs: 500, onFailure: 'skip' },
        ],
        trigger: 'voice',
        enabled: true,
        runCount: 0
      },
      {
        id: 'wf_presentation_mode',
        name: 'Presentation Mode',
        description: 'Prepares system for presentations',
        steps: [
          { id: 's1', action: 'close_app', target: 'whatsapp', delayMs: 0, onFailure: 'skip' },
          { id: 's2', action: 'close_app', target: 'discord', delayMs: 500, onFailure: 'skip' },
          { id: 's3', action: 'close_app', target: 'telegram', delayMs: 500, onFailure: 'skip' },
          { id: 's4', action: 'brightness_control', target: 'set', payload: '90', delayMs: 500, onFailure: 'skip' },
          { id: 's5', action: 'volume_control', target: 'set', payload: '60', delayMs: 500, onFailure: 'skip' },
          { id: 's6', action: 'keyboard_macro', target: 'minimize_all', delayMs: 1000, onFailure: 'skip' },
        ],
        trigger: 'voice',
        enabled: true,
        runCount: 0
      },
      {
        id: 'wf_lock_down',
        name: 'Lock Down',
        description: 'Takes screenshot and locks the system immediately',
        steps: [
          { id: 's1', action: 'screenshot', delayMs: 0, onFailure: 'skip' },
          { id: 's2', action: 'power_control', target: 'lock', delayMs: 1000, onFailure: 'abort' },
        ],
        trigger: 'voice',
        enabled: true,
        runCount: 0
      },
      {
        id: 'wf_cleanup',
        name: 'System Cleanup',
        description: 'Kills resource hogs and clears temp files',
        steps: [
          { id: 's1', action: 'process', target: 'resource_hogs', delayMs: 0, onFailure: 'skip' },
          { id: 's2', action: 'shell_execute', target: 'del /q /s %TEMP%\\*.tmp', delayMs: 2000, onFailure: 'skip' },
        ],
        trigger: 'voice',
        enabled: true,
        runCount: 0
      }
    ];

    for (const wf of builtIns) {
      this.workflows.set(wf.id, wf);
    }
  }

  /**
   * Execute a workflow by ID or name.
   */
  public async executeWorkflow(idOrName: string): Promise<WorkflowResult | null> {
    if (!this.executor) {
      this.log('Workflow engine not connected to bridge', 'error');
      return null;
    }

    // Find workflow by ID or name (case-insensitive)
    let workflow: Workflow | undefined;
    workflow = this.workflows.get(idOrName);
    if (!workflow) {
      for (const [, wf] of this.workflows) {
        if (wf.name.toLowerCase() === idOrName.toLowerCase() ||
            wf.name.toLowerCase().replace(/\s+/g, '_') === idOrName.toLowerCase()) {
          workflow = wf;
          break;
        }
      }
    }

    if (!workflow) {
      this.log(`Workflow not found: ${idOrName}`, 'error');
      return null;
    }

    if (!workflow.enabled) {
      this.log(`Workflow disabled: ${workflow.name}`, 'error');
      return null;
    }

    this.log(`Executing workflow: ${workflow.name}`, 'command');
    const startedAt = new Date().toISOString();
    const stepResults: WorkflowResult['steps'] = [];

    for (const step of workflow.steps) {
      // Check condition
      if (step.condition) {
        const condMet = this.evaluateCondition(step.condition);
        if (!condMet) {
          stepResults.push({
            stepId: step.id,
            action: step.action,
            status: 'skipped',
            result: 'Condition not met',
            duration: 0
          });
          continue;
        }
      }

      // Delay
      if (step.delayMs && step.delayMs > 0) {
        await new Promise(r => setTimeout(r, step.delayMs));
      }

      // Execute
      const stepStart = Date.now();
      let attempts = 0;
      const maxAttempts = step.retries || 1;
      let success = false;
      let resultMsg = '';

      while (attempts < maxAttempts && !success) {
        attempts++;
        try {
          const result = await this.executor({
            action: step.action,
            target: step.target || '',
            payload: step.payload || '',
            extra: step.extra || ''
          });
          resultMsg = result?.message || 'OK';
          success = result?.status !== 'error';
        } catch (e: any) {
          resultMsg = e.message || 'Error';
        }
      }

      stepResults.push({
        stepId: step.id,
        action: step.action,
        status: success ? 'success' : 'failed',
        result: resultMsg,
        duration: Date.now() - stepStart
      });

      this.log(`  Step ${step.id}: ${step.action} ${step.target || ''} → ${success ? 'OK' : 'FAIL'}`, success ? 'success' : 'error');

      // Handle failure policy
      if (!success && step.onFailure === 'abort') {
        this.log('Workflow aborted due to step failure', 'error');
        break;
      }
    }

    // Update workflow stats
    workflow.lastRun = new Date().toISOString();
    workflow.runCount++;

    const allSucceeded = stepResults.every(s => s.status === 'success' || s.status === 'skipped');
    const allFailed = stepResults.every(s => s.status === 'failed');

    const result: WorkflowResult = {
      workflowId: workflow.id,
      workflowName: workflow.name,
      startedAt,
      completedAt: new Date().toISOString(),
      steps: stepResults,
      status: allSucceeded ? 'completed' : allFailed ? 'failed' : 'partial'
    };

    this.log(`Workflow complete: ${workflow.name} (${result.status})`, result.status === 'completed' ? 'success' : 'error');
    return result;
  }

  /**
   * Evaluate a step condition.
   */
  private evaluateCondition(condition: WorkflowStep['condition']): boolean {
    if (!condition) return true;
    
    const now = new Date();
    switch (condition.type) {
      case 'always': return true;
      case 'time_after':
        if (condition.value) {
          const [h, m] = condition.value.split(':').map(Number);
          return now.getHours() > h || (now.getHours() === h && now.getMinutes() >= m);
        }
        return true;
      case 'time_before':
        if (condition.value) {
          const [h, m] = condition.value.split(':').map(Number);
          return now.getHours() < h || (now.getHours() === h && now.getMinutes() < m);
        }
        return true;
      case 'bridge_active':
        return true; // Caller should check bridge status
      default:
        return true;
    }
  }

  /**
   * Register a new custom workflow.
   */
  public addWorkflow(workflow: Omit<Workflow, 'runCount'>): void {
    this.workflows.set(workflow.id, { ...workflow, runCount: 0 });
  }

  /**
   * Get all workflows.
   */
  public getWorkflows(): Workflow[] {
    return Array.from(this.workflows.values());
  }

  /**
   * Find a workflow by name (partial match).
   */
  public findWorkflow(query: string): Workflow | undefined {
    const q = query.toLowerCase();
    for (const [, wf] of this.workflows) {
      if (wf.name.toLowerCase().includes(q) || wf.id.toLowerCase().includes(q)) {
        return wf;
      }
    }
    return undefined;
  }

  /**
   * Get workflow names for the AI to reference.
   */
  public getWorkflowNames(): string[] {
    return Array.from(this.workflows.values()).map(wf => wf.name);
  }

  /**
   * Delete a workflow.
   */
  public removeWorkflow(id: string): boolean {
    return this.workflows.delete(id);
  }

  /**
   * Start the scheduler for time-based workflows.
   */
  public startScheduler(): void {
    if (this.schedulerInterval) return;
    
    this.schedulerInterval = setInterval(() => {
      const now = Date.now();
      for (const [, wf] of this.workflows) {
        if (!wf.enabled || wf.trigger !== 'schedule' || !wf.schedule) continue;

        if (wf.schedule.nextRun && now >= wf.schedule.nextRun) {
          this.executeWorkflow(wf.id);
          
          // Calculate next run
          if (wf.schedule.type === 'interval' && wf.schedule.intervalMs) {
            wf.schedule.nextRun = now + wf.schedule.intervalMs;
          } else if (wf.schedule.type === 'daily' && wf.schedule.time) {
            const [h, m] = wf.schedule.time.split(':').map(Number);
            const next = new Date();
            next.setDate(next.getDate() + 1);
            next.setHours(h, m, 0, 0);
            wf.schedule.nextRun = next.getTime();
          } else {
            wf.enabled = false; // One-shot, disable after run
          }
        }
      }
    }, 30000); // Check every 30 seconds
  }

  /**
   * Stop the scheduler.
   */
  public stopScheduler(): void {
    if (this.schedulerInterval) {
      clearInterval(this.schedulerInterval);
      this.schedulerInterval = null;
    }
  }
}
