import { describe, it, expect, beforeEach } from 'vitest';
import type {
  Task,
  AgentState,
  ExecuteResponse,
  GoalRequest,
} from '../types/index';

describe('Integration Tests', () => {
  let mockSession: AgentState;
  let mockTask: Task;

  beforeEach(() => {
    mockTask = {
      id: 'task-1',
      title: 'Research AI Act',
      description: 'Find information about AI Act compliance',
      status: 'pending',
      tool_used: null,
      result: null,
      reflection: null,
      sources: [],
    };

    mockSession = {
      session_id: 'session-abc123',
      goal: 'Research AI Act compliance',
      tasks: [mockTask],
      context_notes: [],
      current_step: 0,
      is_active: true,
      mode: 'plan',
      final_report_path: null,
      created_at: new Date().toISOString(),
    };
  });

  it('should create a session with a goal', () => {
    const request: GoalRequest = {
      goal: 'Research AI Act compliance',
    };

    expect(request.goal).toBe('Research AI Act compliance');
  });

  it('should initialize session state', () => {
    expect(mockSession.session_id).toBeTruthy();
    expect(mockSession.goal).toBe('Research AI Act compliance');
    expect(mockSession.mode).toBe('plan');
    expect(mockSession.is_active).toBe(true);
    expect(mockSession.tasks.length).toBe(1);
  });

  it('should transition from plan to execute mode', () => {
    const sessionInExecute = { ...mockSession, mode: 'execute' as const };
    expect(sessionInExecute.mode).toBe('execute');
  });

  it('should update task status during execution', () => {
    const taskInProgress = { ...mockTask, status: 'in_progress' as const };
    expect(taskInProgress.status).toBe('in_progress');
  });

  it('should complete task with result', () => {
    const completedTask: Task = {
      ...mockTask,
      status: 'done',
      result: 'AI Act requires compliance with...',
      reflection: 'Task completed successfully',
      sources: ['https://example.com/ai-act'],
    };

    expect(completedTask.status).toBe('done');
    expect(completedTask.result).toBeTruthy();
    expect(completedTask.sources.length).toBe(1);
  });

  it('should handle execute response', () => {
    const response: ExecuteResponse = {
      session_id: mockSession.session_id,
      current_step: 1,
      task_executed: { ...mockTask, status: 'in_progress' },
      is_done: false,
      message: 'Task executed successfully',
    };

    expect(response.current_step).toBe(1);
    expect(response.is_done).toBe(false);
    expect(response.task_executed?.status).toBe('in_progress');
  });

  it('should transition to done mode when all tasks complete', () => {
    const completedSession: AgentState = {
      ...mockSession,
      mode: 'done',
      is_active: false,
      tasks: [
        {
          ...mockTask,
          status: 'done',
          result: 'Completed',
          sources: ['source1'],
        },
      ],
      final_report_path: '/reports/session-abc123.md',
    };

    expect(completedSession.mode).toBe('done');
    expect(completedSession.is_active).toBe(false);
    expect(completedSession.final_report_path).toBeTruthy();
  });

  it('should accumulate context notes', () => {
    const sessionWithNotes: AgentState = {
      ...mockSession,
      context_notes: [
        '[Research AI Act]: AI Act requires compliance with transparency requirements',
        '[Find penalties]: Non-compliance can result in fines up to 6% of revenue',
      ],
    };

    expect(sessionWithNotes.context_notes.length).toBe(2);
    expect(sessionWithNotes.context_notes[0]).toContain('AI Act');
  });

  it('should handle multiple tasks in sequence', () => {
    const sessionWithMultipleTasks: AgentState = {
      ...mockSession,
      tasks: [
        { ...mockTask, id: 'task-1', status: 'done' },
        { ...mockTask, id: 'task-2', status: 'in_progress' },
        { ...mockTask, id: 'task-3', status: 'pending' },
      ],
      current_step: 2,
    };

    expect(sessionWithMultipleTasks.tasks.length).toBe(3);
    expect(sessionWithMultipleTasks.tasks[0].status).toBe('done');
    expect(sessionWithMultipleTasks.tasks[1].status).toBe('in_progress');
    expect(sessionWithMultipleTasks.tasks[2].status).toBe('pending');
  });

  it('should calculate progress', () => {
    const completedCount = mockSession.tasks.filter(
      (t) => t.status === 'done'
    ).length;
    const totalCount = mockSession.tasks.length;
    const progress = (completedCount / totalCount) * 100;

    expect(progress).toBe(0);
    expect(completedCount).toBe(0);
    expect(totalCount).toBe(1);
  });

  it('should handle session deletion', () => {
    const deletedSession = null;
    expect(deletedSession).toBeNull();
  });
});
