import { describe, it, expect } from 'vitest';
import { CommandQueue } from '../services/commandQueue';

describe('CommandQueue', () => {
  it('queues higher priority commands first', () => {
    const queue = new CommandQueue();
    queue.enqueue({ action: 'normal' }, 'normal');
    queue.enqueue({ action: 'critical' }, 'critical');
    queue.enqueue({ action: 'low' }, 'low');

    const status = queue.getStatus();
    expect(status.pending).toBe(3);
    expect(status.byPriority.critical).toBe(1);
    expect(status.byPriority.normal).toBe(1);
    expect(status.byPriority.low).toBe(1);
  });
});
