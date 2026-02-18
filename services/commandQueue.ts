/**
 * Jerry Command Queue Service
 * Queues commands when bridge is offline and replays them when reconnected.
 * Also supports command prioritization and batching.
 */

export interface QueuedCommand {
  id: string;
  command: Record<string, any>;
  priority: 'critical' | 'high' | 'normal' | 'low';
  addedAt: number;
  attempts: number;
  maxRetries: number;
  status: 'queued' | 'executing' | 'completed' | 'failed';
  result?: any;
  onComplete?: (result: any) => void;
  onError?: (error: any) => void;
}

export class CommandQueue {
  private queue: QueuedCommand[] = [];
  private maxSize: number = 100;
  private processing: boolean = false;
  private bridgeSender: ((data: string) => boolean) | null = null;
  private rateLimiter = {
    maxPerSecond: 10,
    tokens: 10,
    lastRefill: Date.now()
  };

  /**
   * Register the bridge sender function.
   */
  public setBridgeSender(sender: (data: string) => boolean): void {
    this.bridgeSender = sender;
  }

  /**
   * Add a command to the queue.
   */
  public enqueue(
    command: Record<string, any>,
    priority: QueuedCommand['priority'] = 'normal',
    maxRetries: number = 3,
    onComplete?: (result: any) => void,
    onError?: (error: any) => void
  ): QueuedCommand {
    const item: QueuedCommand = {
      id: `cmd_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      command,
      priority,
      addedAt: Date.now(),
      attempts: 0,
      maxRetries,
      status: 'queued',
      onComplete,
      onError
    };

    // Insert based on priority
    const priorityOrder = { critical: 0, high: 1, normal: 2, low: 3 };
    const insertIndex = this.queue.findIndex(
      q => priorityOrder[q.priority] > priorityOrder[priority]
    );
    
    if (insertIndex === -1) {
      this.queue.push(item);
    } else {
      this.queue.splice(insertIndex, 0, item);
    }

    // Trim if over max
    if (this.queue.length > this.maxSize) {
      const removed = this.queue.pop();
      if (removed?.onError) removed.onError('Queue overflow: command dropped');
    }

    return item;
  }

  /**
   * Process all queued commands (called when bridge reconnects).
   */
  public async flush(): Promise<{ sent: number; failed: number }> {
    if (!this.bridgeSender || this.processing) return { sent: 0, failed: 0 };
    
    this.processing = true;
    let sent = 0;
    let failed = 0;

    const toProcess = [...this.queue.filter(q => q.status === 'queued')];
    
    for (const item of toProcess) {
      await this.waitForToken();
      item.status = 'executing';
      item.attempts++;

      try {
        const success = this.bridgeSender(JSON.stringify(item.command));
        if (success) {
          item.status = 'completed';
          sent++;
        } else {
          throw new Error('Send failed');
        }
      } catch (e) {
        if (item.attempts >= item.maxRetries) {
          item.status = 'failed';
          failed++;
          if (item.onError) item.onError(e);
        } else {
          item.status = 'queued';
          failed++;
        }
      }

      // Small delay between commands
      await new Promise(r => setTimeout(r, 100));
    }

    // Clean up completed/failed
    this.queue = this.queue.filter(q => q.status === 'queued');
    this.processing = false;
    
    return { sent, failed };
  }

  private refillTokens(): void {
    const now = Date.now();
    const elapsed = (now - this.rateLimiter.lastRefill) / 1000;
    const tokensToAdd = Math.floor(elapsed * this.rateLimiter.maxPerSecond);

    if (tokensToAdd > 0) {
      this.rateLimiter.tokens = Math.min(
        this.rateLimiter.maxPerSecond,
        this.rateLimiter.tokens + tokensToAdd
      );
      this.rateLimiter.lastRefill = now;
    }
  }

  private async waitForToken(): Promise<void> {
    while (true) {
      this.refillTokens();
      if (this.rateLimiter.tokens > 0) {
        this.rateLimiter.tokens--;
        return;
      }
      await new Promise(r => setTimeout(r, 100));
    }
  }

  /**
   * Get queue status.
   */
  public getStatus(): {
    size: number;
    pending: number;
    executing: number;
    byPriority: Record<string, number>;
  } {
    const pending = this.queue.filter(q => q.status === 'queued').length;
    const executing = this.queue.filter(q => q.status === 'executing').length;
    const byPriority: Record<string, number> = { critical: 0, high: 0, normal: 0, low: 0 };
    
    this.queue
      .filter(q => q.status === 'queued')
      .forEach(q => byPriority[q.priority]++);

    return { size: this.queue.length, pending, executing, byPriority };
  }

  /**
   * Clear all queued commands.
   */
  public clear(): void {
    this.queue.forEach(q => {
      if (q.onError) q.onError('Queue cleared');
    });
    this.queue = [];
  }

  /**
   * Get pending count.
   */
  public get pendingCount(): number {
    return this.queue.filter(q => q.status === 'queued').length;
  }
}
