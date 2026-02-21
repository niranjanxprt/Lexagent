import { AgentState, APIKeys, ExecuteResponse, GoalRequest, Session } from '../types';

export type { APIKeys } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function headersWithApiKeys(apiKeys?: APIKeys | null): Record<string, string> {
  const h: Record<string, string> = {};
  if (apiKeys?.openai?.trim()) h['X-OpenAI-API-Key'] = apiKeys.openai.trim();
  if (apiKeys?.tavily?.trim()) h['X-Tavily-API-Key'] = apiKeys.tavily.trim();
  return h;
}

export async function fetchSessions(): Promise<Session[]> {
  try {
    const response = await fetch(`${API_URL}/sessions`);
    if (!response.ok) {
      throw new Error(`Failed to fetch sessions: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching sessions:', error);
    return [];
  }
}

export async function fetchAgentState(sessionId: string): Promise<AgentState | null> {
  try {
    const response = await fetch(`${API_URL}/agent/${sessionId}`);
    if (response.status === 404) {
      return null;
    }
    if (!response.ok) {
      throw new Error(`Failed to fetch agent state: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching agent state:', error);
    if (error instanceof Error && error.message === 'Failed to fetch') {
      throw new Error(
        `Cannot connect to the LexAgent API. Ensure the backend is running at ${API_URL}.`
      );
    }
    throw error;
  }
}

export async function startSession(
  goal: string,
  apiKeys?: APIKeys | null
): Promise<{ session_id: string; state: AgentState }> {
  try {
    const headers = { 'Content-Type': 'application/json', ...headersWithApiKeys(apiKeys) };
    const response = await fetch(`${API_URL}/agent/start`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ goal } as GoalRequest),
    });

    if (!response.ok) {
      let detail = '';
      try {
        const json = await response.json();
        detail = json.detail ?? JSON.stringify(json);
      } catch {
        detail = await response.text();
      }
      throw new Error(detail || `Failed to start session: ${response.status}`);
    }

    const data = await response.json();
    return { session_id: data.session_id, state: data };
  } catch (error) {
    console.error('Error starting session:', error);
    if (error instanceof Error && error.message === 'Failed to fetch') {
      throw new Error(
        `Cannot connect to the LexAgent API. Ensure the backend is running at ${API_URL} and CORS is configured.`
      );
    }
    throw error;
  }
}

export async function executeStep(
  sessionId: string,
  apiKeys?: APIKeys | null
): Promise<ExecuteResponse> {
  try {
    const headers = headersWithApiKeys(apiKeys);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180_000); // 3 min per task
    const response = await fetch(`${API_URL}/agent/${sessionId}/execute`, {
      method: 'POST',
      ...(Object.keys(headers).length ? { headers } : {}),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      let detail = '';
      try {
        const json = await response.json();
        detail = json.detail ?? '';
      } catch {
        detail = await response.text();
      }
      throw new Error(detail || `Failed to execute step: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error executing step:', error);
    if (error instanceof Error && error.message === 'Failed to fetch') {
      throw new Error(
        `Cannot connect to the LexAgent API. Ensure the backend is running at ${API_URL}.`
      );
    }
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timed out. Each task can take 1–2 minutes. Try again.');
    }
    throw error;
  }
}

export async function deleteSession(sessionId: string): Promise<void> {
  try {
    const response = await fetch(`${API_URL}/agent/${sessionId}`, {
      method: 'DELETE',
    });

    if (!response.ok && response.status !== 204) {
      throw new Error(`Failed to delete session: ${response.status}`);
    }
  } catch (error) {
    console.error('Error deleting session:', error);
    throw error;
  }
}

/** Report endpoint returns plain Markdown (text/markdown), not JSON. Use .text() only. */
export async function fetchReport(sessionId: string): Promise<string> {
  try {
    const response = await fetch(`${API_URL}/agent/${sessionId}/report`);
    if (!response.ok) {
      throw new Error(`Failed to fetch report: ${response.statusText}`);
    }
    return await response.text();
  } catch (error) {
    console.error('Error fetching report:', error);
    throw error;
  }
}
