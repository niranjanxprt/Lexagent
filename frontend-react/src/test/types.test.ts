import { describe, it, expect } from 'vitest';
import type {
  Task,
  AgentState,
  ExecuteResponse,
  GoalRequest,
  TaskStatus,
  AgentMode,
} from '../types/index';

describe('Types', () => {
  it('should define Task interface correctly', () => {
    const task: Task = {
      id: '1',
      title: 'Test Task',
      description: 'Test description',
      status: 'pending',
      tool_used: null,
      result: null,
      reflection: null,
      sources: [],
    };

    expect(task.id).toBe('1');
    expect(task.status).toBe('pending');
    expect(task.sources).toEqual([]);
  });

  it('should define AgentState interface correctly', () => {
    const state: AgentState = {
      session_id: 'session-123',
      goal: 'Research AI Act',
      tasks: [],
      context_notes: [],
      current_step: 0,
      is_active: true,
      mode: 'plan',
      final_report_path: null,
      created_at: new Date().toISOString(),
    };

    expect(state.session_id).toBe('session-123');
    expect(state.mode).toBe('plan');
    expect(state.is_active).toBe(true);
  });

  it('should define ExecuteResponse interface correctly', () => {
    const response: ExecuteResponse = {
      session_id: 'session-123',
      current_step: 1,
      task_executed: null,
      is_done: false,
      message: 'Task executed',
    };

    expect(response.is_done).toBe(false);
    expect(response.message).toBe('Task executed');
  });

  it('should define GoalRequest interface correctly', () => {
    const request: GoalRequest = {
      goal: 'Research AI compliance',
    };

    expect(request.goal).toBe('Research AI compliance');
  });

  it('should support TaskStatus type union', () => {
    const statuses: TaskStatus[] = ['pending', 'in_progress', 'done', 'failed'];
    expect(statuses.length).toBe(4);
    expect(statuses).toContain('pending');
  });

  it('should support AgentMode type union', () => {
    const modes: AgentMode[] = ['plan', 'execute', 'done'];
    expect(modes.length).toBe(3);
    expect(modes).toContain('plan');
  });
});
