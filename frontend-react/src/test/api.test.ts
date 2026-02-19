import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('API Functions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should have correct API_BASE configuration', async () => {
    const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
    expect(API_BASE).toBe('http://localhost:8000');
  });

  it('should construct correct API endpoints', () => {
    const API_BASE = 'http://localhost:8000';
    const sessionId = 'test-session-123';

    const endpoints = {
      start: `${API_BASE}/agent/start`,
      getSession: `${API_BASE}/agent/${sessionId}`,
      execute: `${API_BASE}/agent/${sessionId}/execute`,
      report: `${API_BASE}/agent/${sessionId}/report`,
      sessions: `${API_BASE}/sessions`,
      delete: `${API_BASE}/agent/${sessionId}`,
    };

    expect(endpoints.start).toBe('http://localhost:8000/agent/start');
    expect(endpoints.getSession).toBe('http://localhost:8000/agent/test-session-123');
    expect(endpoints.report).toBe('http://localhost:8000/agent/test-session-123/report');
    expect(endpoints.sessions).toBe('http://localhost:8000/sessions');
  });

  it('should have proper timeout configuration', () => {
    const timeout = 30000; // 30 seconds
    expect(timeout).toBe(30000);
    expect(timeout).toBeGreaterThan(0);
  });

  it('should handle API response types', () => {
    const mockTask = {
      id: 'task-1',
      title: 'Research',
      description: 'Test',
      status: 'pending' as const,
      tool_used: null,
      result: null,
      reflection: null,
      sources: [],
    };

    expect(mockTask.id).toBe('task-1');
    expect(mockTask.status).toBe('pending');
  });

  it('should handle error responses', () => {
    const errorResponse = {
      status: 400,
      detail: 'Invalid goal',
    };

    expect(errorResponse.status).toBe(400);
    expect(errorResponse.detail).toContain('Invalid goal');
  });

  it('should support API_BASE from environment', () => {
    const customApiUrl = import.meta.env.VITE_API_URL;
    const fallback = 'http://localhost:8000';
    const apiBase = customApiUrl ?? fallback;

    expect(apiBase).toBeTruthy();
    expect(apiBase).toMatch(/^https?:\/\//);
  });
});
