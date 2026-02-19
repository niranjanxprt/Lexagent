// LexAgent TypeScript types matching backend Pydantic models

export type TaskStatus = 'pending' | 'in_progress' | 'done' | 'failed';
export type AgentMode = 'plan' | 'execute' | 'done';

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  tool_used: string | null;
  result: string | null;
  reflection: string | null;
  sources: string[];
}

export interface AgentState {
  session_id: string;
  goal: string;
  tasks: Task[];
  context_notes: string[];
  current_step: number;
  is_active: boolean;
  mode: AgentMode;
  final_report_path: string | null;
  created_at: string;
}

export type Session = AgentState;

export interface GoalRequest {
  goal: string;
}

export interface ExecuteResponse {
  session_id: string;
  current_step: number;
  task_executed: Task | null;
  is_done: boolean;
  message: string;
}

export interface APIError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}
